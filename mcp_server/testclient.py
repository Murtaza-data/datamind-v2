import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    async with streamablehttp_client("http://127.0.0.1:8000/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Tools:", [t.name for t in tools.tools])

            print("\n--- get_schema ---")
            schema = await session.call_tool("get_schema", {})
            print(schema.content[0].text)

            print("--- run_sql ---")
            result = await session.call_tool("run_sql", {"query": "SELECT COUNT(*) FROM orders;"})
            print(result.content[0].text)

asyncio.run(main())