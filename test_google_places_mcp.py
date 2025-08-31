# test_google_places_mcp_fixed.py
import asyncio
import os
from fastmcp import Client
from mcp_server import mcp

def unwrap_tool_result(result):
    """
    Unwrap the tool result to extract the actual content
    FastMCP returns structured objects that need to be unwrapped
    """
    if hasattr(result, 'content') and result.content:
        # The content is a list containing content objects
        content_object = result.content[0]

        # Check if it has text content
        if hasattr(content_object, 'text'):
            return content_object.text

        # Check if it has JSON content
        if hasattr(content_object, 'json'):
            return content_object.json

    return str(result)

async def test_server():
    """Test the Google Places MCP server"""

    # Test with in-memory client (no network needed)
    async with Client(mcp) as client:
        print("🔍 Testing MCP server connection...")

        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {[tool.name for tool in tools]}")

        # Test the find_attractions_tool
        print("\n🎯 Testing find_attractions_tool...")
        result = await client.call_tool("find_attractions_tool", {
            "city": "Barcelona",
            "country": "Spain"
        })

        # Unwrap the result properly
        content = unwrap_tool_result(result)

        print("✅ Result:")
        # Print first 500 characters
        if len(content) > 500:
            print(content[:500] + "...")
        else:
            print(content)

        print(f"\n📊 Total result length: {len(content)} characters")

if __name__ == "__main__":
    # Set your API key
    # os.environ["GOOGLE_API_KEY"] = "your_api_key_here"

    asyncio.run(test_server())