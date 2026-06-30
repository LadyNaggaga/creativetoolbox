#!/usr/bin/env python3
"""
Local Toolbox with Tool Search emulator.

Serves an MCP-style JSON-RPC endpoint over HTTP so a demo runs with ZERO Azure and zero token.
It faithfully emulates the one behavior the demo is about:

  - when tool search is on, tools/list returns ONLY `tool_search` + `call_tool` (+ pinned tools),
    no matter how many tools are in the box  -> this is what keeps model context flat;
  - `tool_search` REALLY ranks the full box (from tools.json) by keyword overlap over
    description + additional_search_text and returns the matches (the matching is not faked);
  - `call_tool` dispatches to a hero-tool implementation in hero_tools/ (or returns a canned result).

Endpoints (JSON-RPC 2.0 over POST):
  initialize, notifications/initialized, tools/list, tools/call

This mirrors the shape of the real Toolbox MCP endpoint on Foundry closely enough that the agent code
is identical between mock and real modes (only the URL + auth header differ). See references/toolbox-api.md.
"""
import json, os, importlib.util, re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_PATH = os.path.join(HERE, "tools.json")
HERO_DIR = os.path.join(HERE, "hero_tools")
PORT = int(os.environ.get("TOOLBOX_EMULATOR_PORT", "8765"))

with open(TOOLS_PATH) as f:
    BOX = json.load(f)  # {"search_enabled": true, "tools": [{name, description, additional_search_text?, pin?}]}

META_TOOLS = [
    {"name": "tool_search",
     "description": "Describe the capability you need in natural language; returns matching tools.",
     "inputSchema": {"type": "object", "properties": {
         "query": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["query"]}},
    {"name": "call_tool",
     "description": "Invoke a discovered tool by name with arguments.",
     "inputSchema": {"type": "object", "properties": {
         "name": {"type": "string"}, "arguments": {"type": "object"}}, "required": ["name"]}},
]


def _tokens(s):
    return set(re.findall(r"[a-z0-9]+", (s or "").lower()))


def visible_tools():
    """What tools/list returns. With search on: meta-tools + pinned only."""
    if not BOX.get("search_enabled", True):
        return [{"name": t["name"], "description": t.get("description", ""),
                 "inputSchema": {"type": "object"}} for t in BOX["tools"]]
    pinned = [{"name": t["name"], "description": t.get("description", ""),
               "inputSchema": {"type": "object"}} for t in BOX["tools"] if t.get("pin")]
    return META_TOOLS + pinned


def rank(query, limit):
    """Real keyword-overlap ranking over description + additional_search_text."""
    q = _tokens(query)
    scored = []
    for t in BOX["tools"]:
        hay = _tokens(t["name"]) | _tokens(t.get("description", "")) | _tokens(t.get("additional_search_text", ""))
        overlap = len(q & hay)
        if overlap:
            scored.append((overlap, t))
    scored.sort(key=lambda x: (-x[0], x[1]["name"]))
    out = [{"name": t["name"], "description": t.get("description", "")} for _, t in scored[:limit or 5]]
    return out


def call_hero(name, arguments):
    """Dispatch call_tool to hero_tools/<server>_<tool>.py:run(args) if present, else canned text."""
    mod_file = os.path.join(HERO_DIR, name.replace(".", "_") + ".py")
    if os.path.exists(mod_file):
        spec = importlib.util.spec_from_file_location("hero", mod_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.run(arguments or {})
    return f"[mock:{name}] ok (no hero impl; returning canned result for {arguments or {}})"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # quiet
        pass

    def _send(self, obj):
        body = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        n = int(self.headers.get("Content-Length", "0"))
        try:
            req = json.loads(self.rfile.read(n) or "{}")
        except json.JSONDecodeError:
            return self._send({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}})
        method, rid, params = req.get("method"), req.get("id"), req.get("params", {})

        if method == "initialize":
            return self._send({"jsonrpc": "2.0", "id": rid, "result": {
                "protocolVersion": "2025-03-26", "capabilities": {}, "serverInfo": {"name": "toolbox-emulator", "version": "1.0"}}})
        if method == "notifications/initialized":
            return self._send({"jsonrpc": "2.0", "id": rid, "result": {}})
        if method == "tools/list":
            return self._send({"jsonrpc": "2.0", "id": rid, "result": {"tools": visible_tools()}})
        if method == "tools/call":
            name = params.get("name")
            args = params.get("arguments", {})
            if name == "tool_search":
                matches = rank(args.get("query", ""), args.get("limit"))
                return self._send({"jsonrpc": "2.0", "id": rid, "result": {
                    "content": [{"type": "text", "text": json.dumps(matches)}], "structuredContent": {"tools": matches}}})
            if name == "call_tool":
                result = call_hero(args.get("name"), args.get("arguments"))
                return self._send({"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": str(result)}]}})
            # direct call to a pinned/visible tool
            result = call_hero(name, args)
            return self._send({"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": str(result)}]}})
        return self._send({"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": f"method not found: {method}"}})


def box_size():
    return len(BOX["tools"])


def context_size():
    return len(visible_tools())


if __name__ == "__main__":
    print(f"toolbox-emulator: {box_size()} tools in the box, "
          f"{context_size()} in model context (search_enabled={BOX.get('search_enabled', True)})")
    print(f"listening on http://localhost:{PORT}/toolboxes/mars-greenhouse-ops/mcp")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
