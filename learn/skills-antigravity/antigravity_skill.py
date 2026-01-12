"""
Antigravity Skill
功能：返回一个字符串

按照 MCP (Model Context Protocol) 官方规范实现
"""
from mcp.server.fastmcp import FastMCP
from typing import Optional

# 创建 MCP 服务器实例
mcp = FastMCP("Antigravity Skill Server")


@mcp.tool()
def get_antigravity_string(message: Optional[str] = None) -> str:
    """
    返回一个通过 Antigravity 强化的字符串。
    
    这是一个符合 MCP 规范的 skill 实现。
    
    Args:
        message: 可选的消息字符串。
    
    Returns:
        str: 返回的字符串消息
        
    Example:
        >>> get_antigravity_string()
        "Antigravity is working!"
        
        >>> get_antigravity_string("Custom message")
        "Antigravity: Custom message"
    """
    if message:
        return f"Antigravity: {message}"
    return "Antigravity is working!"


if __name__ == "__main__":
    # 运行 MCP 服务器（stdio 模式）
    mcp.run()
