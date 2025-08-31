#!/usr/bin/env python3
"""
MCP Server wrapper using FastMCP
"""

import os
import sys

# Import your existing Google Places code
from google_places_api import find_attractions
from thecrazytourist import search_crazy_tourist

from typing import Dict
from fastmcp import FastMCP

# Create the MCP server using FastMCP
mcp = FastMCP("Find attractions - MCP Server")

@mcp.tool()
def search_crazy_tourist_tool(city: str, country: str) -> Dict:
    """
    Find tourist attractions in a city using Google Places API

    Args:
        city: City name (e.g., 'Barcelona', 'Paris')
        country: Country name (e.g., 'Spain', 'France')

    Returns:
        JSON string with structured attraction data
    """
    if not city:
        raise Exception("City parameter is required")
    if not country:
        raise Exception("Country parameter is required")

    return search_crazy_tourist(city, country)


@mcp.tool()
def find_attractions_tool(city: str, country: str) -> Dict:
    """
    Find tourist attractions in a city using Google Places API

    Args:
        city: City name (e.g., 'Barcelona', 'Paris')
        country: Country name (e.g., 'Spain', 'France')

    Returns:
        JSON string with structured attraction data
    """
    if not city:
        raise Exception("City parameter is required")
    if not country:
        raise Exception("Country parameter is required")

    # Call your existing function
    attractions_list = find_attractions(city, country)

    # Return in Claude-compatible format
    return {
        "attractions": attractions_list
    }

def main():
    """Run the MCP server"""
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY environment variable is required")
        sys.exit(1)

    print("🚀 Starting MCP Server...")
    print("Environment variable required: GOOGLE_API_KEY")
    print("Available tools: find_attractions_tool, search_crazy_tourist_tool")

    # Run the FastMCP server
    mcp.run(transport="http", host="0.0.0.0", port=8081)

if __name__ == "__main__":
    main()