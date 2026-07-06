#!/usr/bin/env python3
"""Local smoke test: connect to the running MCP server over streamable HTTP, list tools, call one.
Usage: python smoke_test.py [http://localhost:8000/mcp]"""
import asyncio
import sys

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/mcp"


async def main():
    async with streamablehttp_client(URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            print(f"tools/list -> {len(tools)} tools")
            for t in tools:
                print(f"  - {t.name}")
            res = await session.call_tool("kb_search_guides", {"args": {"topic": "basil"}})
            print("call kb_search_guides ->", res.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
