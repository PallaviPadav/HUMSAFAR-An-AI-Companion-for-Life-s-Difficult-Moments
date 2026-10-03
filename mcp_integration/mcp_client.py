import asyncio
import sys

from mcp import ClientSession
from mcp.client.stdio import (
    StdioServerParameters,
    stdio_client,
)


async def search_movies_via_mcp(
    query: str,
    limit: int = 5,
):
    """
    Call the HUMSAFAR MCP server through
    the MCP stdio transport.
    """

    server_parameters = StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "mcp_integration.mcp_server",
        ],
    )

    async with stdio_client(server_parameters) as (
        read_stream,
        write_stream,
    ):
        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:
            await session.initialize()

            result = await session.call_tool(
                "search_movies",
                arguments={
                    "query": query,
                    "limit": limit,
                },
            )

            return result


if __name__ == "__main__":
    result = asyncio.run(
        search_movies_via_mcp(
            "3 Idiots",
            limit=1,
        )
    )

    print(result)
