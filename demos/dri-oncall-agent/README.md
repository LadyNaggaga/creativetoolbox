# DRI / On-Call Independent Agent

A governed, Teams-native Foundry agent demo built with **Toolbox with Tool Search on Foundry**, Foundry IQ, Foundry routines, and Work IQ. The agent proactively investigates incidents, drafts mitigation with citations, and requests human approval before any externally visible action.

> **Status:** design + artifact scaffold. Runnable code is scoped to a later phase (see [Implementation phases](#implementation-phases)). Some connectors are marked **preview** or **mock** and must be confirmed in your Foundry project.

## What this demo shows

Loop-engineered enterprise autonomy across four loops:

1. **Agent loop** — reason → call Toolbox tool → observe → continue.
2. **Verification loop** — cross-check hypotheses against telemetry + KB before proposing.
3. **Event / routine loop** — IcM webhooks and Teams events fire the agent in real time; Foundry routines drive schedule- and timer-based follow-ups.
4. **Hill-climbing loop** — routine run history + tool traces + human overrides feed weekly improvements.

Read [`BLOG.md`](./BLOG.md) for a narrative walkthrough of the agent loop with a real incident.

## Scenario at a glance

Friday 14:07 UTC. IcM alert: `payments-api` P2, 5xx rate 18% in `westus2` after a deploy. Alert lands in `#payments-oncall`. Nobody tags anyone. The DRI Agent:

- correlates telemetry with a deploy 20 minutes prior,
- matches a runbook ("5xx after deploy → check idempotency cache"),
- finds the suspect PR and its owner,
- posts a mitigation card with rollback command + validation KQL + **Approve / Decline** buttons,
- on approve, executes with a fresh approval token and verifies recovery,
- schedules a 30-minute follow-up and a 24-hour postmortem draft via Foundry routines.

## Layout

```
dri-oncall-agent/
├── README.md                     # this file
├── BLOG.md                       # Understanding the Agent Loop with Foundry
├── agent-instructions.md         # system/developer instructions for the agent
├── toolbox-tools.json            # Toolbox tool manifest (10 tools)
├── routines/                     # Foundry routines (preview)
│   ├── weekday-readiness-scan.yaml
│   ├── incident-follow-up-30m.yaml
│   ├── postmortem-draft-24h.yaml
│   └── weekly-learning-loop.yaml
├── sample-data/                  # fixtures for the demo
│   ├── incident-alert.json
│   ├── telemetry.jsonl
│   ├── ownership.yaml
│   ├── runbook-payments-5xx.md
│   ├── deploys.jsonl
│   └── pr-8821.json
└── demo-script.md                # presenter talk-track and Teams flow
```

## Architecture

```
Teams channel ──┐
IcM webhook  ───┼──► Event dispatcher ──► Foundry Agent Runtime (DRI Agent)
Foundry routines┘                            │
                                             ├──► Toolbox (Tool Search on Foundry)
                                             │      ├─ search_foundry_iq_kb
                                             │      ├─ query_telemetry_kql
                                             │      ├─ search_work_context (Work IQ)
                                             │      ├─ inspect_recent_changes (GitHub/ADO MCP)
                                             │      ├─ find_service_owner
                                             │      ├─ create_tracking_item        [approval]
                                             │      ├─ draft_mitigation
                                             │      ├─ execute_approved_action     [approval]
                                             │      ├─ schedule_foundry_routine    [approval]
                                             │      └─ inspect_routine_runs
                                             │
                                             └──► Audit sink (App Insights + KQL)
```

## Independent-agent pillars

| Pillar | Implementation |
|---|---|
| **Identity with context** | Entra Agent ID `dri-agent-payments`, tenant-scoped, scoped RBAC (read-only on telemetry/KB/GitHub/ADO; action tools gated by approval token). |
| **Memory & knowledge** | Foundry IQ KB seeded with runbooks, ownership docs, retros, engineering wiki, deploy index. |
| **Proactivity** | IcM webhook + Teams events (real-time); Foundry routines (schedule / timer). |
| **Accountability** | Correlation-ID logging of every tool call, input hash, output digest, approval token, and routine dispatch. Admin kill switch. |

## Implementation phases

| Phase | Scope | Est. |
|---|---|---|
| **MVP** | Local Python agent, mocked Toolbox tools returning fixtures from `sample-data/`, console output, no Teams. | 1–2 days |
| **Connected prototype** | Real Foundry Agent Runtime, live Toolbox with 3 read tools, Teams via Bot Framework, mocked action tools with approval card. | 1 week |
| **Executive demo** | All 10 tools live, IcM webhook trigger, 4 Foundry routines deployed, Entra Agent ID, App Insights audit table, kill switch, evaluation dashboard. | 2–3 weeks |

## Safety rules (excerpt)

- Read-only investigation → verification → mitigation proposal → **approved** execution. Never skip a step.
- No destructive or externally visible action without a fresh `approvalToken`.
- Cite every non-trivial claim (KB source or query text).
- If confidence < 0.6 or sources conflict, state uncertainty and escalate.
- Respect the kill switch: `agent.paused=true` disables all action tools within 30s.

See [`agent-instructions.md`](./agent-instructions.md) for the full instruction set.

## Foundry routines caveats

Routines are **preview**. Minimum interval **5 minutes**. One action per routine. Routine-bound agents require configured **agent identity** — prompt-only agents are insufficient. Confirm regional availability in your Foundry project before deploying.

## Related demos

- [`../pizza-shop-ops`](../pizza-shop-ops) — Toolbox with Tool Search on Foundry, retail ops scenario.
- [`../mars-greenhouse-ops`](../mars-greenhouse-ops) — sensor/actuator loop with governed actions.
- [`../squad-room`](../squad-room) — APIM + APIC governance layer over a Foundry agent.
