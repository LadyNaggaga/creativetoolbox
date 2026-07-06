#!/usr/bin/env python3
"""
Pizza Shop Ops — hero-tools MCP server (cloud).

Exposes the SAME box of tools the local mock demo uses (mock-backends/tools.json) over a real
streamable-HTTP MCP endpoint, so a Foundry Toolbox can wrap it and the hosted agent can drive it
with Tool Search. The 6 hero tools reuse the exact logic from mock-backends/hero_tools/; the rest
are themed stubs so the box is honestly large and Tool Search has real disambiguation to do.

Run locally:
    pip install -r requirements.txt
    python server.py                 # serves MCP at http://localhost:8000/mcp

The Foundry Toolbox points its `mcp` entry at this server's URL (see ../toolbox.yaml).
"""
import importlib.util
import json
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# In the container these live at /app/mock-backends (copied by the Dockerfile). Locally we walk up
# to the demo root. TOOLS_JSON / HERO_DIR can be overridden via env for flexibility.
# In the container these live at /app/mock-backends (copied by the Dockerfile) and PIZZA_MOCK_BACKENDS
# points there. Locally we walk up to the demo root. Compute the local fallback defensively so a
# shallow container path (/app/server.py) never raises before the env override is applied.
_here = Path(__file__).resolve()
_DEMO_ROOT = _here.parents[2] if len(_here.parents) >= 3 else _here.parent  # demos/pizza-shop-ops
_DEFAULT_MOCK = _DEMO_ROOT / "mock-backends"
MOCK_DIR = Path(os.environ.get("PIZZA_MOCK_BACKENDS", str(_DEFAULT_MOCK)))
TOOLS_JSON = MOCK_DIR / "tools.json"
HERO_DIR = MOCK_DIR / "hero_tools"

mcp = FastMCP("pizzashop", stateless_http=True, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))


def _load_hero(tool_name: str):
    """Load the run(args) callable for a hero tool, e.g. 'inventory.check_stock' ->
    hero_tools/inventory_check_stock.py. Returns None if there's no real implementation."""
    fname = tool_name.replace(".", "_") + ".py"
    path = HERO_DIR / fname
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location(fname[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, "run", None)


def _stub_result(tool_name: str, description: str, args: dict) -> str:
    """Themed, deterministic response for the name-only tools in the box."""
    return f"[{tool_name}] ok - {description.split(';')[0].strip()} (args: {json.dumps(args or {})})"


def _register(tool_name: str, description: str):
    """Register one MCP tool. MCP tool names can't carry dots for every client, so we expose the
    underscore form (inventory_check_stock); the human-facing name stays in the description."""
    mcp_name = tool_name.replace(".", "_")
    hero = _load_hero(tool_name)

    def _impl(args: dict | None = None) -> str:
        args = args or {}
        if hero is not None:
            return hero(args)
        return _stub_result(tool_name, description, args)

    _impl.__name__ = mcp_name
    # Tool takes a free-form `args` object so the model can pass whatever the theme needs.
    mcp.add_tool(_impl, name=mcp_name, description=f"{tool_name}: {description}")


def build():
    box = json.loads(TOOLS_JSON.read_text(encoding="utf-8"))
    for t in box["tools"]:
        _register(t["name"], t.get("description", t["name"]))
    return len(box["tools"])


if __name__ == "__main__":
    count = build()
    print(f"pizzashop MCP server: registered {count} tools from {TOOLS_JSON}")
    mcp.run(transport="streamable-http")
