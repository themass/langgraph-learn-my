"""
MCP HTTP/SSE 服务器
用于发布 MCP 服务，可以通过 HTTP 方式调用
"""
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
    print("🚀 Starting MCP HTTP/SSE Server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("🔌 SSE endpoint: http://localhost:8000/sse")
    print("\n按 Ctrl+C 停止服务器\n")
    
    # 使用 SSE 传输模式启动 HTTP 服务器
    mcp.run(transport="sse")
