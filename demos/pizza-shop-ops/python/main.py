#!/usr/bin/env python3
"""
Pizza Shop Ops — a toolbox-demo-builder demo.

Modes:
  (default)  scripted mock — talks to the local emulator; real ranking + real counter, no model key.
  --live     plug in a real model to drive the agent loop (set MODEL_* env vars).
  --real     create a real Toolbox on Foundry and point the agent at it (see toolbox_setup.py).

The magic moment: the box has N tools, the model's context has 2 (tool_search + call_tool).
"""
import argparse, json, os, urllib.request

import activity
import scenario

EMU = os.environ.get("TOOLBOX_MCP_ENDPOINT",
                     f"http://localhost:{os.environ.get('TOOLBOX_EMULATOR_PORT', '8765')}/toolboxes/pizza-shop-ops/mcp")
TOOLS_JSON = os.path.join(os.path.dirname(__file__), "..", "mock-backends", "tools.json")


def rpc(method, params=None, _id=[0]):
    _id[0] += 1
    payload = json.dumps({"jsonrpc": "2.0", "id": _id[0], "method": method, "params": params or {}}).encode()
    headers = {"Content-Type": "application/json", "Foundry-Features": "Toolboxes=V1Preview"}
    # real mode adds Authorization here (DefaultAzureCredential, scope https://ai.azure.com/.default)
    if os.environ.get("TOOLBOX_BEARER"):
        headers["Authorization"] = f"Bearer {os.environ['TOOLBOX_BEARER']}"
    req = urllib.request.Request(EMU, data=payload, headers=headers)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def list_tools():
    return rpc("tools/list")["result"]["tools"]


def search(query, limit=5):
    res = rpc("tools/call", {"name": "tool_search", "arguments": {"query": query, "limit": limit}})
    return json.loads(res["result"]["content"][0]["text"])


def call(name, arguments):
    res = rpc("tools/call", {"name": "call_tool", "arguments": {"name": name, "arguments": arguments}})
    return res["result"]["content"][0]["text"]


def run_scripted():
    rpc("initialize")
    rpc("notifications/initialized")

    box_size = len(json.load(open(TOOLS_JSON))["tools"])
    visible = list_tools()
    pinned = max(0, len(visible) - 2)  # everything beyond the 2 meta-tools is pinned/visible
    activity.header("Pizza Shop Ops")
    activity.counter(box_size, len(visible), pinned)

    round_trip = 0
    for turn in scenario.TURNS:
        activity.user(turn["user"])
        round_trip += 1
        activity.tool_search(turn["intent"], round_trip)
        matches = search(turn["intent"])
        activity.matched([m["name"] for m in matches])
        c = turn["call"]
        activity.call_tool(c["name"], c["arguments"])
        activity.result(call(c["name"], c["arguments"]))

    # the box never changed size; the context never grew.
    activity.counter(box_size, len(list_tools()), pinned)


def run_live():
    raise SystemExit("LIVE mode: wire a real model + Microsoft Agent Framework here "
                     "(see references/toolbox-api.md §5). Then let the model emit tool_search/call_tool itself.")


def run_real():
    raise SystemExit("REAL mode: run `python toolbox_setup.py` to create the Foundry toolbox, "
                     "set TOOLBOX_MCP_ENDPOINT + TOOLBOX_BEARER, then run --live against it.")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--live", action="store_true")
    p.add_argument("--real", action="store_true")
    a = p.parse_args()
    (run_live if a.live else run_real if a.real else run_scripted)()
