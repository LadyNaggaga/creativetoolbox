# Mars Greenhouse Ops — Cloud (hosted agent on Foundry)

The [local mock demo](../README.md) runs a day in the dome offline with `make demo`. This folder takes
the **same box of tools to the cloud**: the hero tools run as a real MCP server on Azure Container
Apps, a **Foundry Toolbox** wraps them with **Tool Search**, and a **hosted agent** keeps the
greenhouse with a live model — the model itself writes the `tool_search` queries and a power
rebalance pauses for a real approval.

```
hosted agent  ──►  Foundry Toolbox (tool_search + call_tool)  ──►  ACA MCP server (32 greenhouse tools)
                        + web_search
```

## Prerequisites

- Azure subscription + the hosted-agent toolchain: `az`, `azd`, and the `azd ai` (Microsoft Foundry)
  extension. See the [hosted agent quickstart prerequisites](https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-hosted-agent#prerequisites).
- `az login` done. **No local Docker needed** — the MCP image builds in ACR.

## 1. Deploy the hero-tools MCP server (Azure Container Apps)

```pwsh
cd demos/mars-greenhouse-ops
./cloud/infra/deploy.ps1 -ResourceGroup rg-mars-cloud -Location eastus
```

This builds `cloud/mcp-server/` in ACR (server-side) and deploys it to Container Apps. Copy the
printed **MCP endpoint** (e.g. `https://marsgreenhouse-mcp.<hash>.eastus.azurecontainerapps.io/mcp`).

Paste it into `cloud/toolbox.yaml` as the `marsgreenhouse` entry's `server_url`.

> On Windows, `az acr build` may print a cosmetic `cp1252` UnicodeEncodeError while streaming logs —
> the build still succeeds server-side. Verify with `az acr task list-runs --registry <acr>` and run
> the ACR-create / build / deployment steps manually if `deploy.ps1` halts on that error.

## 2. Scaffold the hosted agent

```pwsh
azd ai agent init `
  -m "https://github.com/microsoft-foundry/foundry-samples/blob/main/samples/python/hosted-agents/agent-framework/responses/04-foundry-toolbox/agent.manifest.yaml" `
  --src src/mars-greenhouse-ops
```
Pick your project/model when prompted; choose **1 core, 2Gi** for the container tier. Then customize
`main.py` (the dome instructions) and set `agent.yaml`'s `name: mars-greenhouse-ops`.

## 3. Create the toolbox

```pwsh
azd env set FOUNDRY_PROJECT_ENDPOINT "$(azd env get-value AZURE_AI_PROJECT_ENDPOINT)"
azd ai toolbox create mars-greenhouse-ops --from-file ./cloud/toolbox.yaml
```
Copy the **versioned MCP endpoint** it prints.

## 4. Provision + run locally

Set these in `src/mars-greenhouse-ops/.env` (see `cloud/.env.example`):

```
AZURE_AI_MODEL_DEPLOYMENT_NAME=<your-model-deployment>
TOOLBOX_ENDPOINT=<versioned-endpoint-from-step-3>
```

```pwsh
azd provision
azd ai agent run        # serves the agent at http://localhost:8088
# In another terminal — a day in the dome, driven by the live model:
azd ai agent invoke --local "Prepping bed 3 for basil. How deep do I sow the seeds and what spacing?"
azd ai agent invoke --local "Rebalance the dome power load to shed non-critical draw"   # <- approval gate fires
```

## 5. Deploy the agent

```pwsh
azd env set TOOLBOX_ENDPOINT "<versioned-endpoint-from-step-3>"
azd deploy
azd ai agent invoke "What's the CO2 and humidity in the dome right now?"
```

## What to watch for (the cloud magic moment)

- The model writes its **own** `tool_search` queries — no scripted intents. Watch the traces in
  Application Insights (auto-wired) to see the exact query it chose and which tool ranked first.
- The box has **32 tools + web_search**; the model's context stays at the two meta-tools (plus the
  pinned `sensors_read_air` air readout).
- `power_balance_load` carries `require_approval: always` — the live invoke **pauses** for a crew-lead
  sign-off before it sheds load. That's the governance beat.

## Clean up

```pwsh
azd ai toolbox delete mars-greenhouse-ops --force
azd down                                            # agent + Foundry resources
az group delete --name rg-mars-cloud --yes          # the MCP server (ACA + ACR)
```

## Notes

- The MCP server has **public ingress and no auth** for demo simplicity. For a governed setup (front
  with API Management + register in an Azure API Center private MCP registry), see the `squad-room`
  cloud demo.
- If `azd provision` fails resolving your principal against a stale subscription, provision the Bicep
  directly with `az deployment sub create --location eastus2 --template-file cloud/agent/infra/main.bicep
  --parameters @cloud/agent/infra/main.az.params.json`, then sync the outputs into the azd env.
- Per-tool `require_approval` in `tool_configs` is a preview surface — if the platform only honors
  entry-level approval, move `power_balance_load` into its own `mcp` entry with `require_approval: always`.
