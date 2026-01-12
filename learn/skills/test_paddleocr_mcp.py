"""
测试 PaddleOCR MCP 服务

使用方法：
1. 命令行测试（直接运行 MCP 服务）：
   python3 test_paddleocr_mcp.py

2. 测试 Cursor 配置（模拟 Cursor 调用）：
   python3 test_paddleocr_mcp.py --cursor-mode
"""

import asyncio
import sys
import os
import json
from pathlib import Path
from typing import Optional

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("❌ 错误: 缺少 'mcp' 模块")
    print("请安装: pip install mcp")
    sys.exit(1)


async def test_paddleocr_mcp(cursor_mode: bool = False):
    """测试 PaddleOCR MCP 服务"""
    
    # 从 Cursor 配置读取参数
    if cursor_mode:
        config_path = Path.home() / ".cursor" / "mcp.json"
        if not config_path.exists():
            print(f"❌ 未找到 Cursor MCP 配置文件: {config_path}")
            print("请先配置 Cursor MCP 服务")
            return
        
        with open(config_path) as f:
            config = json.load(f)
        
        paddleocr_config = config.get("mcpServers", {}).get("PaddleOCR-VL")
        if not paddleocr_config:
            print("❌ 未找到 PaddleOCR-VL 配置")
            return
        
        command = paddleocr_config.get("command")
        args = paddleocr_config.get("args", [])
        env = paddleocr_config.get("env", {})
        
        print(f"📋 从 Cursor 配置读取:")
        print(f"   Command: {command}")
        print(f"   Args: {args}")
        print(f"   Env: {json.dumps(env, indent=2, ensure_ascii=False)}")
        print()
        
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env
        )
    else:
        # 直接测试模式（使用环境变量）
        python_path = "/Users/liguoqing/.pyenv/versions/3.12.1/bin/python3"
        env = {
            "PADDLEOCR_MCP_PIPELINE": "PaddleOCR-VL",
            "PADDLEOCR_MCP_PPOCR_SOURCE": "aistudio",
            "PADDLEOCR_MCP_SERVER_URL": "https://a7l51bc4t3qfm6o6.aistudio-app.com",
            "PADDLEOCR_MCP_AISTUDIO_ACCESS_TOKEN": "8fe361bcf0a2c5eae5ad6c250ce916972ef7c53e",
            "PADDLEOCR_MCP_TIMEOUT": "120"
        }
        
        print(f"📋 直接测试模式:")
        print(f"   Python: {python_path}")
        print(f"   Env: {json.dumps(env, indent=2, ensure_ascii=False)}")
        print()
        
        server_params = StdioServerParameters(
            command=python_path,
            args=["-m", "paddleocr_mcp"],
            env=env
        )
    
    print("🔗 正在连接到 PaddleOCR MCP 服务...\n")
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 初始化会话
                await session.initialize()
                print("✅ MCP 服务连接成功！\n")
                
                # 列出可用工具
                print("📋 正在获取可用工具...")
                tools = await session.list_tools()
                print(f"✅ 可用工具数量: {len(tools.tools)}")
                for tool in tools.tools:
                    print(f"   - {tool.name}: {tool.description}")
                print()
                
                # 测试工具调用（如果有图片）
                if tools.tools:
                    # 查找 OCR 相关工具
                    ocr_tools = [t for t in tools.tools if "ocr" in t.name.lower() or "paddle" in t.name.lower()]
                    
                    if ocr_tools:
                        tool_name = ocr_tools[0].name
                        print(f"🔧 测试工具: {tool_name}")
                        print("   注意: 需要提供图片路径或 URL 才能完整测试")
                        print("   示例调用:")
                        print(f'   await session.call_tool("{tool_name}", {{"input_data": "图片路径或URL"}})')
                        print()
                    else:
                        print("⚠️  未找到 OCR 相关工具")
                else:
                    print("⚠️  没有可用工具")
                
                print("✅ 测试完成！")
                
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def test_with_image(image_path: str, cursor_mode: bool = False):
    """使用图片测试 OCR 功能"""
    
    if not os.path.exists(image_path):
        print(f"❌ 图片不存在: {image_path}")
        return
    
    print(f"🖼️  使用图片测试: {image_path}\n")
    
    # 读取配置（与上面相同的逻辑）
    if cursor_mode:
        config_path = Path.home() / ".cursor" / "mcp.json"
        with open(config_path) as f:
            config = json.load(f)
        paddleocr_config = config.get("mcpServers", {}).get("PaddleOCR-VL")
        command = paddleocr_config.get("command")
        args = paddleocr_config.get("args", [])
        env = paddleocr_config.get("env", {})
    else:
        python_path = "/Users/liguoqing/.pyenv/versions/3.12.1/bin/python3"
        env = {
            "PADDLEOCR_MCP_PIPELINE": "PaddleOCR-VL",
            "PADDLEOCR_MCP_PPOCR_SOURCE": "aistudio",
            "PADDLEOCR_MCP_SERVER_URL": "https://a7l51bc4t3qfm6o6.aistudio-app.com",
            "PADDLEOCR_MCP_AISTUDIO_ACCESS_TOKEN": "8fe361bcf0a2c5eae5ad6c250ce916972ef7c53e",
            "PADDLEOCR_MCP_TIMEOUT": "120"
        }
        command = python_path
        args = ["-m", "paddleocr_mcp"]
    
    server_params = StdioServerParameters(
        command=command,
        args=args,
        env=env if not cursor_mode else paddleocr_config.get("env", {})
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # 获取工具
                tools = await session.list_tools()
                ocr_tools = [t for t in tools.tools if "ocr" in t.name.lower() or "paddle" in t.name.lower()]
                
                if not ocr_tools:
                    print("❌ 未找到 OCR 工具")
                    return
                
                tool_name = ocr_tools[0].name
                print(f"🔧 调用工具: {tool_name}")
                print(f"📤 输入: {image_path}\n")
                
                # 调用工具
                result = await session.call_tool(
                    tool_name,
                    arguments={
                        "input_data": image_path,
                        "output_mode": "simple"  # 使用简单模式获取可读结果
                    }
                )
                
                print(f"📋 结果类型: {type(result)}")
                print(f"📋 结果属性: {dir(result)}")
                
                if result.content:
                    print("\n✅ OCR 结果:")
                    for i, content in enumerate(result.content):
                        print(f"\n--- 内容块 {i+1} ---")
                        print(f"类型: {type(content)}")
                        if hasattr(content, 'text'):
                            print(f"文本内容:\n{content.text}")
                        elif hasattr(content, 'type'):
                            print(f"内容类型: {content.type}")
                            if hasattr(content, 'text'):
                                print(f"文本内容:\n{content.text}")
                        # 打印所有属性
                        print(f"所有属性: {[attr for attr in dir(content) if not attr.startswith('_')]}")
                else:
                    print("⚠️  未返回结果")
                    print(f"结果对象: {result}")
                    
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="测试 PaddleOCR MCP 服务")
    parser.add_argument(
        "--cursor-mode",
        action="store_true",
        help="使用 Cursor 配置文件中的设置"
    )
    parser.add_argument(
        "--image",
        type=str,
        help="测试图片路径（可选）"
    )
    
    args = parser.parse_args()
    
    if args.image:
        # 测试图片 OCR
        asyncio.run(test_with_image(args.image, args.cursor_mode))
    else:
        # 基本连接测试
        success = asyncio.run(test_paddleocr_mcp(args.cursor_mode))
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    main()
