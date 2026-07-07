# DRI Agent — Demo Script

**Duration:** ~5 minutes live, or a 60-second highlight cut.  
**Setup:** Teams channel `#payments-oncall`, DRI Agent installed and paused=false.  
**Mode:** all Toolbox tools point at `sample-data/` fixtures.

---

## Beat 1 — Cold open (10s)

> "This is a Teams channel for the payments on-call rotation. Nobody's watching it right now. Watch what happens when an incident fires and **I don't tag anyone**."

Trigger the IcM alert (replay `sample-data/incident-alert.json`).

---

## Beat 2 — Proactive investigation (25s)

Agent posts within ~3 seconds in-thread:

> **DRI Agent** — Investigating **IcM-4471293** (payments-api, westus2, 5xx 18%). Read-only tools only until approval. Correlating with recent changes now.

Then, within ~15s, a **findings card**:

- **Telemetry** (query text visible): 5xx rate rose from ~0.3% to 18% at 13:50 UTC, five minutes after deploy `v2.14.3` at 13:47 UTC. *(cite: fabric-iq query)*
- **Runbook match:** *"Payments 5xx after deploy → check idempotency cache."* *(cite: runbook-payments-5xx.md, section "Common causes / 1")*
- **Suspect change:** PR #8821 *"Refactor idempotency-key cache TTL"* by @alicez, merged 13:41 UTC. TTL changed from sliding 10m to fixed 2m.
- **Owner:** @alicez (primary), @rmehta (secondary). Source: `ownership.yaml`.
- **Confidence:** **High** — 3 corroborating sources.

> "Notice: **cited**, **verifiable**, **read-only**. The agent hasn't touched production."

---

## Beat 3 — Mitigation proposal (30s)

Agent posts a **mitigation card**:

- **Action:** Rollback `payments-api` from `v2.14.3` → `v2.14.2` in `westus2`.
- **Command** (verbatim, from runbook step 1).
- **Blast radius:** 1 service, 1 region, ~10k RPS.
- **Validation KQL:** the diagnostic query from the runbook. Will re-run 2 minutes after action.
- **Sources:** runbook §Mitigation/1, deploys.jsonl `dep-20260706-payments-api-2143`, PR #8821.
- **Buttons:** `Approve` / `Decline`.

> "This is the **verification loop** meeting the **approval gate**. The agent is proposing, not acting."

---

## Beat 4 — Approve and execute (30s)

Click **Approve**. Card returns a fresh `approvalToken` and the approver identity.

Agent replies:

> Executing rollback with approval token `apr_7f…c2`, approved by @dchen at 14:09 UTC. Audit ID `aud_20260706_14091`.

Two minutes later:

> Recovery verified. 5xx rate is 0.4% and falling. *(query text visible)*  
> Scheduled follow-ups: `incident-follow-up-30m` at 14:37 UTC, `postmortem-draft-24h` at 14:09 UTC + 24h.

> "**Every step** — proposal, approval, execution, verification, follow-up scheduling — is logged with a correlation ID."

---

## Beat 5 — Routines and accountability (30s)

Open the **Foundry routines** view.

- `weekday-readiness-scan` (schedule).
- `incident-follow-up-30m` (timer, just scheduled).
- `postmortem-draft-24h` (timer, just scheduled).
- `weekly-learning-loop` (schedule).

Open the run history for `incident-follow-up-30m` from a previous incident.

> "Run history is the **accountability surface**. Every dispatch, response ID, status, and error is inspectable. This is how the hill-climbing loop learns."

---

## Beat 6 — Close (15s)

> "Four loops. **Agent** — reason and act. **Verification** — cross-check with citations. **Event and routine** — proactive triggers and follow-ups. **Hill-climbing** — the agent gets better every week from its own run history and human corrections. That's a **loop-engineered enterprise agent** on **Toolbox with Tool Search on Foundry**."

---

## 60-second highlight cut

Beats 1 → 2 (findings card) → 3 (mitigation card) → 4 (approve + recovery) → 6 (closing line). Skip beat 5 unless the audience is technical.
