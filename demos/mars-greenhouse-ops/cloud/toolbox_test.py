"""Smoke-test the deployed Mars Greenhouse Ops toolbox (Tool Search on).

Usage:
    python toolbox_test.py "<TOOLBOX_ENDPOINT>" "how deep to sow basil"

Proves: tools/list shows only tool_search + call_tool (Tool Search hides the box),
and tool_search surfaces the hero MCP tools through the ACA server.
"""
import json
import subprocess
import sys

import httpx

TB = sys.argv[1]
QUERY = sys.argv[2] if len(sys.argv) > 2 else "how deep to sow basil"

token = subprocess.run(
    ["az", "account", "get-access-token", "--resource", "https://ai.azure.com",
     "--query", "accessToken", "-o", "tsv"],
    capture_output=True, text=True, shell=True,
).stdout.strip()

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
    "Foundry-Features": "Toolboxes=V1Preview",
}


def rpc(client, sid, method, params, _id):
    h = dict(headers)
    if sid:
        h["Mcp-Session-Id"] = sid
    r = client.post(TB, headers=h, json={
        "jsonrpc": "2.0", "id": _id, "method": method, "params": params})
    new_sid = r.headers.get("Mcp-Session-Id", sid)
    body = r.text
    # streamable-http may return SSE frames
    for line in body.splitlines():
        if line.startswith("data:"):
            body = line[5:].strip()
            break
    try:
        return json.loads(body), new_sid
    except Exception:
        return {"raw": body}, new_sid


with httpx.Client(timeout=60) as client:
    init, sid = rpc(client, None, "initialize", {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "smoke", "version": "1"},
    }, 1)
    # notifications/initialized
    h = dict(headers)
    if sid:
        h["Mcp-Session-Id"] = sid
    client.post(TB, headers=h, json={
        "jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})

    lst, sid = rpc(client, sid, "tools/list", {}, 2)
    names = [t["name"] for t in lst.get("result", {}).get("tools", [])]
    print("tools/list ->", names)

    res, sid = rpc(client, sid, "tools/call", {
        "name": "tool_search", "arguments": {"query": QUERY}}, 3)
    print("\ntool_search(", QUERY, ") ->")
    print(json.dumps(res.get("result", res), indent=2)[:2000])
