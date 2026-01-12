"""
MCP HTTP 客户端
用于调用发布的 MCP HTTP/SSE 服务器
"""
import asyncio
import sys
from mcp import ClientSession
from mcp.client.sse import sse_client

async def run():
    # MCP HTTP/SSE 服务器地址
    server_url = "http://localhost:8000/sse"
    
    print(f"🔗 Connecting to MCP server at: {server_url}")
    print("⏳ Waiting for server connection...\n")

    async with sse_client(server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List tools
            tools = await session.list_tools()
            print(f"✅ Available tools: {[tool.name for tool in tools.tools]}")

            # Call tool
            print(f"\n🔧 Calling tool 'test_output_name' with name='World'...")
            result = await session.call_tool("test_output_name", arguments={"name": "World"})
            
            # Print result
            if result.content:
                print(f"✅ Tool Result: {result.content[0].text}")
            else:
                print("⚠️  Tool Result: No content returned")

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except ImportError as e:
        print(f"❌ Error: Missing module. {e}")
        print("💡 Please install dependencies: pip install -r requirements.txt")
    except ConnectionError as e:
        print(f"❌ Error: Cannot connect to server. {e}")
        print("💡 Make sure the server is running: python3 server_http.py")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()

