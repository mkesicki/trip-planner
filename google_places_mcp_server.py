#!/usr/bin/env python3
"""
MCP Server wrapper for Google Places API using FastMCP
File: google_places_mcp_server.py
"""

import os
import sys

# Import your existing Google Places code
from google_places_api import find_attractions
from typing import Dict

#from mcp.server.fastmcp import FastMCP
from fastmcp import FastMCP

# Create the MCP server using FastMCP
mcp = FastMCP("Google Places MCP Server")

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

    # if attractions:
    #     # Format the response for n8n
    #     location_text = f"{city} {country}".strip()

    #     # Create structured data for n8n processing
    #     structured_data = {
    #         "city": location_text,
    #         "total_attractions": len(attractions),
    #         "attractions": attractions
    #     }

    #     # Add human-readable summary
    #     response_text = f"🎯 Found {len(attractions)} attractions in {location_text}:\n\n"

    #     for i, attraction in enumerate(attractions[:10], 1):  # Show first 10 in summary
    #         rating_text = f"{attraction['rating']}/5 ({attraction['review_count']} reviews)" if attraction['rating'] else "No rating"

    #         response_text += f"{i}. {attraction['name']}\n"
    #         response_text += f"   📊 Rating: {rating_text}\n"
    #         response_text += f"   📍 Address: {attraction['address']}\n"
    #         response_text += f"   🏷️  Types: {', '.join(attraction['types']) if attraction['types'] else 'N/A'}\n"
    #         if attraction['website']:
    #             response_text += f"   🌐 Website: {attraction['website']}\n"
    #         if attraction['google_maps_url']:
    #             response_text += f"   🗺️  Google Maps: {attraction['google_maps_url']}\n"
    #         response_text += "\n"

    #     if len(attractions) > 10:
    #         response_text += f"... and {len(attractions) - 10} more attractions\n\n"

    #     response_text += f"📋 STRUCTURED DATA (for n8n processing):\n{json.dumps(structured_data, indent=2)}"

    #     return response_text
    # else:
    #     return f"❌ No attractions found in {city} {country}".strip()

def main():
    """Run the MCP server"""
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY environment variable is required")
        sys.exit(1)

    print("🚀 Starting Google Places MCP Server...")
    print("Environment variable required: GOOGLE_API_KEY")
    print("Available tools: find_attractions_tool")

    # Run the FastMCP server
    mcp.run(transport="http", host="0.0.0.0", port=8081)

if __name__ == "__main__":
    main()