from mcp.server.fastmcp import FastMCP
from tools.execute import register_tools as register_execute_tools
from tools.credentials import register_tools as register_credential_tools
from tools.interactive import register_tools as register_interactive_tools
from tools.device import register_tools as register_device_tools
from resources import register_vendor_resources


# Initialize MCP server named NetworkConsole
mcp = FastMCP("NetworkConsole")

# Register all tool modules
register_execute_tools(mcp)
register_credential_tools(mcp)
register_interactive_tools(mcp)
register_device_tools(mcp)

# Register vendor command table resources
register_vendor_resources(mcp)

if __name__ == "__main__":
    mcp.run(transport="stdio")
