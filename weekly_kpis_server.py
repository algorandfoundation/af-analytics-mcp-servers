from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("Maria")

# Import Tools 
from tools.kpis import *

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')