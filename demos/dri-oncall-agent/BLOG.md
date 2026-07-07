# Understanding the Agent Loop with Foundry — a DRI Agent, Step by Step

*How Toolbox with Tool Search on Foundry, Foundry IQ, and Foundry routines turn "a model that calls tools" into a **governed enterprise coworker** — traced through a real Friday-afternoon incident.*

---

## Why "the agent loop" is the whole story

Everyone can wire a language model to a couple of tools. The interesting question isn't *"can it call a tool?"* — it's:

- Does it **know when to stop investigating and propose**?
- Does it **verify** its own hypothesis before recommending a rollback?
- Does it wait for a **human approval** before touching production?
- Can you **inspect** what it did, later, in a way that satisfies audit?
- Does it get **better next week** without a human re-writing its prompt?

Those questions aren't answered by "the model." They're answered by **the loop around the model**. That harness — reason, act, verify, wait, learn — is what we call the **agent loop**, and on **Toolbox with Tool Search on Foundry** it's not a diagram, it's a set of concrete surfaces you can build against.

This post walks the loop through one real incident and shows exactly which Foundry primitive does what.

The scenario, the tools, the routines, and the fixtures used in this walkthrough all live in [`demos/dri-oncall-agent/`](./README.md).

---

## The scenario

**Friday, 14:07 UTC.** An IcM alert fires: `payments-api` is throwing 5xx errors at 18% in `westus2`. The alert lands in `#payments-oncall`. It's a Teams channel with about 40 people in it. Nobody has responded yet.

Then this appears in the thread, three seconds later:

> **DRI Agent** — Investigating **IcM-4471293** (payments-api, westus2, 5xx 18%). Read-only tools only until approval. Correlating with recent changes now.

Nobody tagged the agent. Nobody typed a prompt. And by the time an on-call engineer has finished re-reading the alert, the agent has already correlated the spike with a deploy from 20 minutes ago, matched a runbook, identified a suspect PR, resolved the owner, and posted a mitigation proposal — with citations — waiting for a human to click **Approve**.

That's four loops running at once. Let's take them one at a time.

---

## Loop 1 — the agent loop

**Reason → call one tool → observe → decide → repeat.**

This is the innermost loop, and it's the one people usually mean when they say "agent." On Foundry Agent Runtime it looks like this:

```
             ┌──────────────────────────────┐
             │  Foundry Agent Runtime       │
             │  (reason step)               │
             └─────────────┬────────────────┘
                           │  tool call
                           ▼
             ┌──────────────────────────────┐
             │  Toolbox with Tool Search    │
             │  on Foundry                  │
             │                              │
             │  routes to the right tool    │
             │  based on the request        │
             └─────────────┬────────────────┘
                           │  observation
                           ▼
                    back to reason step
```

The critical Foundry piece here isn't the model — it's **Tool Search on Toolbox**. The agent doesn't need to be handed a hard-coded list of ten tool names. It expresses intent ("I need to check recent deployments for payments-api in the last 30 minutes"), and Toolbox routes to the right tool with the right shape.

For our incident, the agent's inner monologue reads like this (heavily paraphrased):

1. *"I have an IcM alert. First thing I should know: what changed recently?"*  → calls `inspect_recent_changes(serviceName="payments-api", timeRange="PT30M")`. Gets back deploy `v2.14.3` at 13:47 UTC, merged from PR #8821.
2. *"Deploy correlates in time. But correlation isn't cause. Let me see if the runbook has a known pattern for 5xx-after-deploy."* → `search_foundry_iq_kb(query="payments-api 5xx after deploy", filters={source: ["runbook"]})`. Gets a hit: "Common causes / 1 — Idempotency-key cache misconfiguration."
3. *"The suspect PR touched idempotency cache TTL. That's a direct match."* → `search_foundry_iq_kb` again for retros. Finds `retro-2025-11-18 — idempotency TTL regression`.
4. *"I have a plausible cause with a corroborated runbook and a matching prior retro. Who owns this?"* → `find_service_owner(serviceName="payments-api")`. Gets @alicez.
5. *"Enough to propose. Draft the mitigation."* → `draft_mitigation(...)`.

Notice the discipline: **one tool at a time**, each observation gates the next decision. That discipline lives in the agent instructions ([`agent-instructions.md`](./agent-instructions.md)):

> Reason → call **one** Toolbox tool → observe → decide next step. Do not batch action tools.

Batching action tools is where naive agents get themselves into trouble. This one can't, by construction.

---

## Loop 2 — the verification loop

**Every non-trivial claim must be cited. Every action must be validated after the fact.**

This is what turns an "agent that answers" into an "agent you can trust in production." It sits *inside* the agent loop but has its own contract:

- No claim without a citation object `{source, title, url, updatedAt, confidence}`.
- Telemetry claims must include the **exact query text**.
- Confidence < 0.6 or conflicting sources → escalate, don't act.
- Every action tool must be followed by a **validation** step: re-run the diagnostic query, confirm recovery.

In our incident, this is why the mitigation card doesn't just say "roll back v2.14.3." It says:

- **Action:** rollback `payments-api` from `v2.14.3` → `v2.14.2` in `westus2`.
- **Blast radius:** 1 service, 1 region, ~10k RPS.
- **Sources:** runbook §Mitigation/1, deploys.jsonl `dep-20260706-payments-api-2143`, PR #8821.
- **Validation KQL** (verbatim from runbook): re-run 2 minutes after execution.
- **Buttons:** `Approve` / `Decline`.

And it's why, two minutes after the rollback, the agent posts a follow-up:

> Recovery verified. 5xx rate is 0.4% and falling. *(query text visible)*

The verification loop is what closes the gap between "the model believes this worked" and "we can prove it worked."

**The Foundry primitive doing the heavy lifting here is Foundry IQ Knowledge Base.** Every citation the agent produces traces back to a chunk with a stable URL, a section anchor, and an `updatedAt` timestamp. If the runbook changes tomorrow, the agent's next incident cites the new version — and the old citation still resolves to the version the agent read.

---

## Loop 3 — the event and routine loop

**The agent doesn't wait to be talked to.**

This is where Foundry-native surfaces make the difference between "an agent" and "an agent that behaves like a coworker on rotation." Two mechanisms:

**Real-time triggers.** Teams events, IcM webhooks, ADO/GitHub events, telemetry alerts. Our IcM alert doesn't go into a queue that the agent polls — it fires the agent directly. Three-second time-to-first-message isn't a benchmark, it's a consequence of not polling.

**Foundry routines (preview).** For things that happen on a schedule or at a specific future time. In our demo we deploy four:

| Routine | Trigger | Purpose |
|---|---|---|
| `weekday-readiness-scan` | schedule, 08:00 PST weekdays | Post open incidents, risky deploys, stale alerts, unresolved action items. |
| `incident-follow-up-30m` | timer, +30m from incident create | Verify owner ack, mitigation progress, status-update cadence. Nudge if any is missed. |
| `postmortem-draft-24h` | timer, +24h from resolve | Draft a postmortem for human review. Never publishes. |
| `weekly-learning-loop` | schedule, Monday 09:00 PST | Analyze last 7 days and recommend improvements. |

Here's what makes routines interesting for the loop story: **they're not just cron.** Each routine's action is *"invoke this agent with this prompt,"* which means the routine inherits every guardrail the agent already has — instructions, tool policy, approval gates, citation contract, audit trail. You don't have to re-implement safety for the scheduler.

A concrete example: when the incident is resolved, our agent doesn't email the team a postmortem template. It calls `schedule_foundry_routine` (an action tool, so it requires approval) to create a **one-shot timer** 24 hours out. When the timer fires, the same agent, with the same instructions, produces a *draft* postmortem in-thread and marks it clearly as a draft. If the team doesn't like it, the fix goes into the agent's instructions or the KB, and next week's postmortem inherits the fix.

A caveat worth stating out loud, because it appears in the routine YAMLs too: routines are **preview**, minimum interval is 5 minutes, each routine has one action, and routine-bound agents require **configured agent identity** (a prompt-only agent won't work). Confirm regional availability in your Foundry project before deploying.

Peek at [`routines/incident-follow-up-30m.yaml`](./routines/incident-follow-up-30m.yaml) if you want to see how tight the manifest is — 30 lines of YAML for a fully governed, agent-invoking, timer-triggered follow-up.

---

## Loop 4 — the hill-climbing loop

**The agent gets better every week without you re-writing its prompt.**

The other three loops are inside a single incident. This one lives *between* incidents. It's the loop that most demos skip and most production deployments miss.

Three inputs feed it:

1. **Tool-call traces.** Every call has an input hash, an output digest, a duration, a correlation ID. The agent emits a `tool_call_trace` block at the end of every incident reply.
2. **Routine run history.** `inspect_routine_runs` returns dispatch ID, response ID, status, phase, error summary for every routine dispatch. That's the accountability surface — for humans, for audit, and for the agent's own weekly analysis.
3. **Human corrections.** Declined approvals. Manual overrides. Edits to the postmortem draft. Emoji reactions on the readiness-scan post. All of it captured with correlation.

On Monday morning, `weekly-learning-loop` fires. The **same agent** analyzes its own last seven days and posts a ranked list of recommended changes:

- Agent-instruction diffs (proposed).
- Toolbox tool description or schema changes.
- Foundry IQ KB gaps — missing runbook sections, stale docs.
- Safety rubric additions.
- Retry / escalation policy tweaks.

Crucially, the agent **does not apply the changes**. A human reviews the ranked list. The good ones ship. The bad ones don't. That's hill-climbing with a human in the loop — the same governance discipline that makes the other three loops safe.

The output is compounding: an agent that behaves the same as last week is fine; an agent that behaves *better* than last week is a coworker.

---

## Putting the four loops in one picture

```
                           ┌────── hill-climbing loop (weekly) ──────┐
                           │                                          │
                           ▼                                          │
                     ┌───────────┐   traces / run history / overrides │
                     │  Human    │◄─────────────────────────────────  │
                     │  reviewer │                                    │
                     └─────┬─────┘                                    │
        approves ships     │                                          │
                           ▼                                          │
              ┌───────────────────────┐                               │
              │  DRI Agent            │                               │
              │  (Foundry Agent       │                               │
              │   Runtime)            │                               │
              │                       │  ← event / routine loop:      │
              │  ┌─── agent loop ──┐  │    IcM webhook, Teams event,  │
              │  │ reason → tool → │  │    Foundry routine schedule,  │
              │  │ observe → …     │  │    or one-shot timer.         │
              │  └────────┬────────┘  │                               │
              │           ▼           │                               │
              │  ┌── verification ──┐ │                               │
              │  │ cite + validate  │ │                               │
              │  └────────┬─────────┘ │                               │
              └───────────┼───────────┘                               │
                          │                                          │
                          ▼                                          │
              ┌───────────────────────┐                              │
              │  Approval card in     │                              │
              │  Teams (fresh token)  │                              │
              └───────────┬───────────┘                              │
                          │  action                                  │
                          ▼                                          │
              ┌───────────────────────┐   audit                      │
              │  Toolbox (action tool)│───►───────────────────────►──┘
              └───────────────────────┘
```

Each loop has a distinct job. Each is anchored to a specific Foundry primitive:

- **Agent loop** → Foundry Agent Runtime + Toolbox with Tool Search.
- **Verification loop** → Foundry IQ Knowledge Base + explicit citation contract.
- **Event / routine loop** → Teams / IcM / webhook events + Foundry routines.
- **Hill-climbing loop** → routine run history + audit trail + human review.

Take any one of these out and you have a demo. Put all four together, with an identity (Entra Agent ID), scoped tool permissions, and a kill switch, and you have something you can actually put on a Teams channel that 40 real people are watching.

---

## Try it

Everything above is buildable today (routines in preview) against the artifacts in [`demos/dri-oncall-agent/`](./README.md):

- [`agent-instructions.md`](./agent-instructions.md) — the full instruction set.
- [`toolbox-tools.json`](./toolbox-tools.json) — the ten-tool Toolbox manifest with schemas.
- [`routines/*.yaml`](./routines/) — the four Foundry routine manifests.
- [`sample-data/*`](./sample-data/) — the exact fixtures used in this walkthrough. Point your MVP at these first.
- [`demo-script.md`](./demo-script.md) — the presenter script if you want to record the 60-second cut.

Phase it in: MVP with mocked tools against `sample-data/`, then a connected prototype in Teams with three live tools, then the full ten tools with the four routines deployed and an App Insights audit table wired up.

The loop is the product. Toolbox with Tool Search on Foundry is what makes the loop cheap enough to build, safe enough to ship, and inspectable enough to trust.
