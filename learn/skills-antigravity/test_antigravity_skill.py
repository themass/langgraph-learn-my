import asyncio
import sys
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_skill():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[os.path.join(os.path.dirname(__file__), "antigravity_skill.py")],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 列出可用的 skills/tools
            tools = await session.list_tools()
            print(f"Available skills: {[tool.name for tool in tools.tools]}")
            
            # 调用 skill（不传参数，使用默认值）
            result = await session.call_tool("get_antigravity_string", arguments={})
            print(f"Result default: {result.content[0].text}")
            
            # 调用 skill（传入自定义消息）
            result = await session.call_tool("get_antigravity_string", arguments={"message": "Floating freely"})
            print(f"Result custom: {result.content[0].text}")

if __name__ == "__main__":
    asyncio.run(test_skill())
