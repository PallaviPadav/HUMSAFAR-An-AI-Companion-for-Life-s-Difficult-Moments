import asyncio
import sys

from mcp import ClientSession
from mcp.client.stdio import (
    StdioServerParameters,
    stdio_client,
)


def get_server_parameters():
    """Configure the existing HUMSAFAR MCP server."""

    return StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "mcp_integration.mcp_server",
        ],
    )


async def call_mcp_tool(
    tool_name: str,
    arguments: dict,
):
    """
    Connect to the HUMSAFAR MCP server and call
    the specified tool with the supplied arguments.
    """

    server_parameters = get_server_parameters()

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
                tool_name,
                arguments=arguments,
            )

            return result


async def search_movies_via_mcp(
    query: str,
    limit: int = 5,
):
    """Call the movie-search MCP tool."""

    return await call_mcp_tool(
        tool_name="search_movies",
        arguments={
            "query": query,
            "limit": limit,
        },
    )


async def search_inspirational_videos_via_mcp(
    query: str,
    limit: int = 5,
):
    """Search for inspirational videos through MCP."""

    return await call_mcp_tool(
        tool_name="search_inspirational_videos",
        arguments={
            "query": query,
            "limit": limit,
        },
    )


if __name__ == "__main__":

    async def main():
        print("Testing inspirational-video MCP search...")

        result = await search_inspirational_videos_via_mcp(
            query="motivational stories overcoming failure",
            limit=3,
        )

        print(result)

    asyncio.run(main())
