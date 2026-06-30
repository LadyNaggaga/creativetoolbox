#!/usr/bin/env python3
"""
--real mode: create the actual Toolbox version on Foundry with Tool Search enabled, then print the
consumer endpoint. Verified API shapes are in references/toolbox-api.md (§3-4). Requires a Foundry
project + deployed model and `pip install azure-ai-projects azure-identity`.

Build the FULL box from mock-backends/tools.json so the real toolbox matches the demo. For tools
that are real MCP servers you host, set server_url/project_connection_id. For the canned hero tools,
either stand up a tiny MCP server or keep them as a single themed MCP server you control.
"""
import json, os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

ENDPOINT = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
SLUG = "pizza-shop-ops"
TOOLS_JSON = os.path.join(os.path.dirname(__file__), "..", "mock-backends", "tools.json")


def build_tools():
    box = json.load(open(TOOLS_JSON))
    tools = [{"type": "toolbox_search_preview"}]  # MUST be first — enables tool search
    # Group hero tools under one themed MCP server you host; real servers get their own entry.
    server_url = os.environ.get("THEME_MCP_SERVER_URL", "https://your-theme-mcp.example.com")
    tool_configs = {}
    for t in box["tools"]:
        cfg = {}
        if t.get("pin"):
            cfg["pin"] = True
        if t.get("additional_search_text"):
            cfg["additional_search_text"] = t["additional_search_text"]
        if cfg:
            tool_configs[t["name"].split(".", 1)[-1]] = cfg
    tools.append({
        "type": "mcp", "server_label": SLUG.replace("-", ""),
        "server_url": server_url, "require_approval": "never",
        "tool_configs": tool_configs,
    })
    return tools


def main():
    project = AIProjectClient(endpoint=ENDPOINT, credential=DefaultAzureCredential())
    version = project.beta.toolboxes.create_toolbox_version(
        toolbox_name=SLUG,
        description="Pizza Shop Ops — built by toolbox-demo-builder, tool search enabled",
        tools=build_tools(),
    )
    print(f"created toolbox '{version.name}' version {version.version}")
    print("consumer endpoint:")
    print(f"  {ENDPOINT}/toolboxes/{SLUG}/mcp?api-version=v1")
    print("set TOOLBOX_MCP_ENDPOINT to that, get a bearer token "
          "(scope https://ai.azure.com/.default) into TOOLBOX_BEARER, then run: python main.py --live")


if __name__ == "__main__":
    main()
