import anyio
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def main() -> None:
    url = "http://localhost:8000/mcp"

    async with streamable_http_client(url) as (read_stream, write_stream, _get_session_id):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # 1) Ask the server which tools are available (tools/list).
            tools_result = await session.list_tools()
            print("Tools:")
            for t in tools_result.tools:
                print(f"- {t.name}: {t.description}")

            # 2) Call a specific tool by name with JSON-like arguments (tools/call).
            result = await session.call_tool("add_numbers", {"a": 9, "b": 3})
            print("\nadd_numbers result:")
            print(result.content)


if __name__ == "__main__":
    anyio.run(main)

