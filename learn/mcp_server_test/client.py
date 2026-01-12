import asyncio
import sys
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run():
    # Get absolute path to the server script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_script = os.path.join(current_dir, "server.py")
    
    print(f"Connecting to server at: {server_script}")

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_script],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List tools
            tools = await session.list_tools()
            print(f"\nAvailable tools: {[tool.name for tool in tools.tools]}")

            # Call tool
            print(f"\nCalling tool 'test_output_name' with name='World'...")
            result = await session.call_tool("test_output_name", arguments={"name": "World"})
            
            # Print result
            if result.content:
                print(f"Tool Result: {result.content[0].text}")
            else:
                print("Tool Result: No content returned")

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except ImportError:
        print("Error: 'mcp' module not found. Please install it using: pip install mcp")
    except Exception as e:
        print(f"An error occurred: {e}")
