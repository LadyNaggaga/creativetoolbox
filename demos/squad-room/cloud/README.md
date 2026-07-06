# Squad Room — Cloud (hosted agent on Foundry)

The [local mock demo](../README.md) runs the "add dark mode, shipped by a team" story offline with
`make demo`. This folder takes the **same box of tools to the cloud**: the 48 hero tools run as a real
MCP server on Azure Container Apps, a **Foundry Toolbox** wraps them with **Tool Search**, and a
**hosted agent** answers for whoever is talking — lead, researcher, or builder. The model itself writes
the `tool_search` queries and a governed `releases.cut` pauses for a real lead approval.

```
lead / researcher / builder  ──►  hosted agent  ──►  Foundry Toolbox (tool_search + call_tool)  ──►  ACA MCP server (48 dev tools)
                                                          + web_search
```

## Prerequisites

- Azure subscription + the hosted-agent toolchain: `az`, `azd`, and the `azd ai` (Microsoft Foundry)
  extension. See the [hosted agent quickstart prerequisites](https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-hosted-agent#prerequisites).
- `az login` done. **No local Docker needed** — the MCP image builds in ACR.

## 1. Deploy the hero-tools MCP server (Azure Container Apps)

```pwsh
cd demos/squad-room
./cloud/infra/deploy.ps1 -ResourceGroup rg-squad-cloud -Location eastus
```

This builds `cloud/mcp-server/` in ACR (server-side) and deploys it to Container Apps. Copy the
printed **MCP endpoint** (e.g. `https://squadroom-mcp.<hash>.eastus.azurecontainerapps.io/mcp`).

Paste it into `cloud/toolbox.yaml` as the `squadroom` entry's `server_url`.

> On Windows, `az acr build` may print a cosmetic `cp1252` UnicodeEncodeError while streaming logs —
> the build still succeeds server-side. Verify with `az acr task list-runs --registry <acr>` and run
> the ACR-create / build / deployment steps manually if `deploy.ps1` halts on that error.

## 2. Scaffold the hosted agent

```pwsh
azd ai agent init `
  -m "https://github.com/microsoft-foundry/foundry-samples/blob/main/samples/python/hosted-agents/agent-framework/responses/04-foundry-toolbox/agent.manifest.yaml" `
  --src src/squad-room
```
Pick your project/model when prompted; choose **1 core, 2Gi** for the container tier. Then customize
`main.py` (the three-role squad instructions) and set `agent.yaml`'s `name: squad-room`.

## 3. Create the toolbox

```pwsh
azd env set FOUNDRY_PROJECT_ENDPOINT "$(azd env get-value AZURE_AI_PROJECT_ENDPOINT)"
azd ai toolbox create squad-room --from-file ./cloud/toolbox.yaml
```
Copy the **versioned MCP endpoint** it prints.

## 4. Provision + run locally

Set these in `src/squad-room/.env` (see `cloud/.env.example`):

```
AZURE_AI_MODEL_DEPLOYMENT_NAME=<your-model-deployment>
TOOLBOX_ENDPOINT=<versioned-endpoint-from-step-3>
```

```pwsh
azd provision
azd ai agent run        # serves the agent at http://localhost:8088
# In another terminal — three roles, one box, driven by the live model:
azd ai agent invoke --local "Find how theming is currently done in this codebase."
azd ai agent invoke --local "Open a pull request that adds a dark palette to the ThemeProvider."
azd ai agent invoke --local "Cut a release with the dark mode change."   # <- approval gate fires
```

## 5. Deploy the agent

```pwsh
azd env set TOOLBOX_ENDPOINT "<versioned-endpoint-from-step-3>"
azd deploy
azd ai agent invoke "Find how theming is currently done in this codebase."
```

> On this machine, the shell injects a stray `AZURE_ENV_NAME` that hijacks the azd default env. Before
> `azd deploy`, in the same shell: set `$env:AZURE_ENV_NAME` to the real env (`squad-room-<suffix>`),
> reset `.azure/config.json`'s `defaultEnvironment`, delete any stray env folder, and pin
> `AZURE_TENANT_ID` / `AZURE_SUBSCRIPTION_ID` so azd doesn't enumerate a dead subscription.

## What to watch for (the cloud magic moment)

- Each role writes its **own** `tool_search` query — no scripted intents. Watch the traces in
  Application Insights (auto-wired) to see the exact query it chose and which tool ranked first:
  `find how theming is done` → `kb_search_docs`, `open a pull request` → `repo_open_pr`,
  `cut a release` → `releases_cut`.
- The box has **48 tools + web_search**; every member's context stays at the two meta-tools.
- `releases_cut` carries `require_approval: always` — the live invoke **pauses** for a lead sign-off
  before it ships. That's the governance beat, and because it lives on the box it covers the whole team.

## Clean up

```pwsh
azd ai toolbox delete squad-room --force
azd down                                             # agent + Foundry resources
az group delete --name rg-squad-cloud --yes          # the MCP server (ACA + ACR)
```

## Notes

- The MCP server has **public ingress and no auth** for demo simplicity. The flagship governance
  upgrade for this demo is to front the ACA server with **API Management** and register it in an
  **Azure API Center private MCP registry**, then point the toolbox `server_url` at the governed
  gateway URL — the team's agents discover only approved tools, with audit and access control on top.
- If `azd provision` fails resolving your principal against a stale subscription, provision the Bicep
  directly with `az deployment sub create --location eastus2 --template-file cloud/agent/infra/main.bicep
  --parameters @cloud/agent/infra/main.az.params.json`, then sync the outputs into the azd env.
- Per-tool `require_approval` in `tool_configs` is a preview surface — if the platform only honors
  entry-level approval, move `releases_cut` into its own `mcp` entry with `require_approval: always`.
