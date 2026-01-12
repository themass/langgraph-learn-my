#!/usr/bin/env python3
"""
从 Cursor 上传的图片进行 OCR 识别

支持多种输入方式：
1. 本地文件路径
2. HTTP/HTTPS URL
3. Base64 编码的图片数据
"""

import asyncio
import sys
import os
import json
import base64
from pathlib import Path
from typing import Optional

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("❌ 错误: 缺少 'mcp' 模块")
    print("请安装: pip install mcp")
    sys.exit(1)


async def ocr_image(input_data: str, use_cursor_config: bool = True):
    """
    使用 PaddleOCR-VL 识别图片中的文字
    
    Args:
        input_data: 图片路径、URL 或 Base64 字符串
        use_cursor_config: 是否使用 Cursor 配置文件
    """
    
    # 读取配置
    if use_cursor_config:
        config_path = Path.home() / ".cursor" / "mcp.json"
        if not config_path.exists():
            print(f"❌ 未找到 Cursor MCP 配置文件: {config_path}")
            return None
        
        with open(config_path) as f:
            config = json.load(f)
        
        paddleocr_config = config.get("mcpServers", {}).get("PaddleOCR-VL")
        if not paddleocr_config:
            print("❌ 未找到 PaddleOCR-VL 配置")
            return None
        
        command = paddleocr_config.get("command")
        args = paddleocr_config.get("args", [])
        env = paddleocr_config.get("env", {})
    else:
        # 直接模式
        command = "/Users/liguoqing/.pyenv/versions/3.12.1/bin/python3"
        args = ["-m", "paddleocr_mcp"]
        env = {
            "PADDLEOCR_MCP_PIPELINE": "PaddleOCR-VL",
            "PADDLEOCR_MCP_PPOCR_SOURCE": "aistudio",
            "PADDLEOCR_MCP_SERVER_URL": "https://a7l51bc4t3qfm6o6.aistudio-app.com",
            "PADDLEOCR_MCP_AISTUDIO_ACCESS_TOKEN": "8fe361bcf0a2c5eae5ad6c250ce916972ef7c53e",
            "PADDLEOCR_MCP_TIMEOUT": "120"
        }
    
    server_params = StdioServerParameters(
        command=command,
        args=args,
        env=env
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
                    return None
                
                tool_name = ocr_tools[0].name
                print(f"🔧 使用工具: {tool_name}")
                print(f"📤 输入: {input_data[:100]}..." if len(input_data) > 100 else f"📤 输入: {input_data}")
                print()
                
                # 调用工具
                result = await session.call_tool(
                    tool_name,
                    arguments={
                        "input_data": input_data,
                        "output_mode": "simple",
                        "return_images": False
                    }
                )
                
                # 提取文本内容
                text_content = []
                if result.content:
                    for content in result.content:
                        if hasattr(content, 'text') and content.text:
                            text_content.append(content.text)
                        elif hasattr(content, 'type') and content.type == 'text':
                            if hasattr(content, 'text'):
                                text_content.append(content.text)
                
                return '\n'.join(text_content) if text_content else None
                
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="使用 PaddleOCR-VL 识别图片文字")
    parser.add_argument(
        "input",
        type=str,
        help="图片路径、URL 或 Base64 字符串"
    )
    parser.add_argument(
        "--no-cursor-config",
        action="store_true",
        help="不使用 Cursor 配置文件"
    )
    
    args = parser.parse_args()
    
    result = asyncio.run(ocr_image(args.input, use_cursor_config=not args.no_cursor_config))
    
    if result:
        print("\n" + "="*60)
        print("✅ OCR 识别结果:")
        print("="*60)
        print(result)
        print("="*60)
    else:
        print("\n❌ OCR 识别失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
