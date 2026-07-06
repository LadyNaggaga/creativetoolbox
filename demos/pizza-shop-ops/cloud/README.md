# Pizza Shop Ops — Cloud (hosted agent on Foundry)

The [local mock demo](../README.md) runs the Friday rush offline with `make demo`. This folder takes
the **same box of tools to the cloud**: the hero tools run as a real MCP server on Azure Container
Apps, a **Foundry Toolbox** wraps them with **Tool Search**, and a **hosted agent** drives the rush
with a live model — the model itself writes the `tool_search` queries and the oven pauses for a real
approval.

```
hosted agent  ──►  Foundry Toolbox (tool_search + call_tool)  ──►  ACA MCP server (18 pizza tools)
                        + web_search
```

## Prerequisites

- Azure subscription + the hosted-agent toolchain: `az`, `azd`, and the `azd ai` (Microsoft Foundry)
  extension. See the [hosted agent quickstart prerequisites](https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-hosted-agent#prerequisites).
- `az login` done. **No local Docker needed** — the MCP image builds in ACR.

## 1. Deploy the hero-tools MCP server (Azure Container Apps)

```pwsh
cd demos/pizza-shop-ops
./cloud/infra/deploy.ps1 -ResourceGroup rg-pizza-cloud -Location eastus
```

This builds `cloud/mcp-server/` in ACR (server-side) and deploys it to Container Apps. Copy the
printed **MCP endpoint** (e.g. `https://pizzashop-mcp.<hash>.eastus.azurecontainerapps.io/mcp`).

Paste it into `cloud/toolbox.yaml` as the `pizzashop` entry's `server_url`.

## 2. Scaffold the hosted agent

```pwsh
azd ai agent init `
  -m "https://github.com/microsoft-foundry/foundry-samples/blob/main/samples/python/hosted-agents/agent-framework/responses/04-foundry-toolbox/agent.manifest.yaml" `
  --src src/pizza-agent
```
Pick your project/model when prompted; choose **1 core, 2Gi** for the container tier.

## 3. Create the toolbox

```pwsh
azd env set FOUNDRY_PROJECT_ENDPOINT "$(azd env get-value AZURE_AI_PROJECT_ENDPOINT)"
azd ai toolbox create pizza-shop-ops --from-file ./cloud/toolbox.yaml
```
Copy the **versioned MCP endpoint** it prints.

## 4. Provision + run locally

Set these in `src/pizza-agent/.env` (see `cloud/.env.example`):

```
AZURE_AI_MODEL_DEPLOYMENT_NAME=<your-model-deployment>
TOOLBOX_ENDPOINT=<versioned-endpoint-from-step-3>
```

```pwsh
azd provision
azd ai agent run        # serves the agent at http://localhost:8088
# In another terminal — the Friday rush, driven by the live model:
azd ai agent invoke --local "Friday rush is kicking off — are we good on mozzarella?"
azd ai agent invoke --local "fire up the deck oven for Neapolitan pies"   # <- approval gate fires
```

## 5. Deploy the agent

```pwsh
azd env set TOOLBOX_ENDPOINT "<versioned-endpoint-from-step-3>"
azd deploy
azd ai agent invoke "table 12 wants a large pepperoni, get it in"
```

## What to watch for (the cloud magic moment)

- The model writes its **own** `tool_search` queries — no scripted intents. Watch the traces in
  Application Insights (auto-wired) to see the exact query it chose and which tool ranked first.
- The box has **18 tools + web_search**; the model's context stays at the two meta-tools.
- `oven_set_temp` carries `require_approval: always` — the live invoke **pauses** for a shift-lead
  sign-off before it fires. That's the governance beat.

## Clean up

```pwsh
azd ai toolbox delete pizza-shop-ops --force
azd down                                            # agent + Foundry resources
az group delete --name rg-pizza-cloud --yes         # the MCP server (ACA + ACR)
```

## Notes

- The MCP server has **public ingress and no auth** for demo simplicity. For a governed setup (front
  with API Management + register in an Azure API Center private MCP registry), see the `squad-room`
  cloud demo.
- Per-tool `require_approval` in `tool_configs` is a preview surface — if the platform only honors
  entry-level approval, move `oven_set_temp` into its own `mcp` entry with `require_approval: always`.
