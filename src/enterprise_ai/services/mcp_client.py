"""MCP Streamable HTTP client. Servers must be explicitly configured and trusted."""
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def list_remote_tools(server_url: str) -> list[dict]:
    async with streamablehttp_client(server_url) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.list_tools()
            return [{"name": item.name, "description": item.description or "",
                     "input_schema": item.inputSchema} for item in result.tools]

async def call_remote_tool(server_url: str, tool_name: str, arguments: dict) -> dict:
    async with streamablehttp_client(server_url) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return {"is_error": bool(result.isError),
                    "content": [{"type": item.type, "text": getattr(item, "text", "")}
                                for item in result.content]}
