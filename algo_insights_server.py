from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("Paul")

# Import Tools 
from tools.algo_insights import *

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')