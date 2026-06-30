#!/usr/bin/env python3
"""
The Squad Room — a toolbox-demo-builder demo.

A whole AI TEAM (lead / researcher / builder) shares ONE governed Toolbox. Each member fires its own
tool_search against the same box; the box stays a single flat-cost surface and every member's context
is just the 2 meta-tools. The point: bring ANY agent or agent-team (Squad, Agent Framework, Copilot,
custom) to the same endpoint the same way.

Modes:
  (default)  scripted mock — members talk to the local emulator; real ranking + real counter, no key.
  --live     give each member its own Squad/agent loop driving tool_search itself.
  --real     create a real Toolbox on Foundry and point the team at it (see toolbox_setup.py).
"""
import argparse, json, os, urllib.request

import activity
import scenario

EMU = os.environ.get("TOOLBOX_MCP_ENDPOINT",
                     f"http://localhost:{os.environ.get('TOOLBOX_EMULATOR_PORT', '8765')}/toolboxes/squad-room/mcp")
TOOLS_JSON = os.path.join(os.path.dirname(__file__), "..", "mock-backends", "tools.json")


def rpc(method, params=None, _id=[0]):
    _id[0] += 1
    payload = json.dumps({"jsonrpc": "2.0", "id": _id[0], "method": method, "params": params or {}}).encode()
    headers = {"Content-Type": "application/json", "Foundry-Features": "Toolboxes=V1Preview"}
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
    team = sorted({t["member"] for t in scenario.TURNS})
    activity.header("The Squad Room")
    activity.counter(box_size, len(visible), len(team))

    round_trip = 0
    for turn in scenario.TURNS:
        activity.member(turn["member"], turn["user"])
        round_trip += 1
        activity.tool_search(turn["intent"], round_trip)
        matches = search(turn["intent"])
        activity.matched([m["name"] for m in matches])
        c = turn["call"]
        activity.call_tool(c["name"], c["arguments"])
        activity.result(call(c["name"], c["arguments"]))

    # one shared box; every member's context stayed at the 2 meta-tools.
    activity.counter(box_size, len(list_tools()), len(team))


def run_live():
    raise SystemExit("LIVE mode: give each team member its own Squad/agent loop "
                     "(see references/squad-integration.md + toolbox-api.md §5), all pointed at the "
                     "same toolbox endpoint, and let each member emit tool_search/call_tool itself.")


def run_real():
    raise SystemExit("REAL mode: run `python toolbox_setup.py` to create the Toolbox on Foundry, "
                     "set TOOLBOX_MCP_ENDPOINT + TOOLBOX_BEARER, then run --live against it.")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--live", action="store_true")
    p.add_argument("--real", action="store_true")
    a = p.parse_args()
    (run_live if a.live else run_real if a.real else run_scripted)()
