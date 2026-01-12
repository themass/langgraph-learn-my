from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Simple Server")

@mcp.tool()
def test_output_name(name: str) -> str:
    """
    Test tool that returns 'testOutput' + name.
    
    Args:
        name: The name to append to the output string.
    """
    return "testOutput" + name

if __name__ == "__main__":
    mcp.run()
