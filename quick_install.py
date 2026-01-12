#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangGraph 学习项目快速安装脚本
用于快速安装核心依赖包
"""

import subprocess
import sys
import os
from typing import List, Tuple

def run_command(command: str, description: str = "") -> bool:
    """运行命令并返回是否成功"""
    if description:
        print(f"🔧 {description}")
    
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {description} - 成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - 失败")
        print(f"错误信息: {e.stderr}")
        return False

def check_python_version() -> bool:
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 需要 Python 3.8 或更高版本")
        return False
    print(f"✅ Python 版本: {version.major}.{version.minor}.{version.micro}")
    return True

def install_core_dependencies() -> bool:
    """安装核心依赖"""
    core_packages = [
        "langgraph",
        "langchain", 
        "langchain-core",
        "langchain-community",
        "langchain-openai",
        "langchain-ollama",
        "openai",
        "requests"
    ]
    
    print("📦 安装核心依赖包...")
    for package in core_packages:
        if not run_command(f"pip install {package}", f"安装 {package}"):
            return False
    return True

def install_optional_dependencies() -> bool:
    """安装可选依赖"""
    optional_packages = [
        "streamlit",
        "gradio", 
        "fastapi",
        "uvicorn[standard]",
        "chromadb",
        "sentence-transformers",
        "pandas",
        "numpy"
    ]
    
    print("📦 安装可选依赖包...")
    for package in optional_packages:
        run_command(f"pip install {package}", f"安装 {package}")
    return True

def verify_installation() -> bool:
    """验证安装"""
    print("🔍 验证关键依赖安装...")
    
    test_imports = [
        ("langgraph", "LangGraph"),
        ("langchain", "LangChain"),
        ("openai", "OpenAI"),
        ("requests", "Requests")
    ]
    
    for module, name in test_imports:
        try:
            __import__(module)
            print(f"✅ {name} 导入成功")
        except ImportError:
            print(f"❌ {name} 导入失败")
            return False
    
    return True

def main():
    """主函数"""
    print("🚀 LangGraph 学习项目快速安装脚本")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 检查是否在虚拟环境中
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 当前在虚拟环境中")
    else:
        print("⚠️  建议在虚拟环境中安装依赖")
        response = input("是否继续安装? (y/N): ")
        if response.lower() != 'y':
            print("安装已取消")
            sys.exit(0)
    
    # 升级pip
    run_command("pip install --upgrade pip", "升级 pip")
    
    # 安装核心依赖
    if not install_core_dependencies():
        print("❌ 核心依赖安装失败")
        sys.exit(1)
    
    # 安装可选依赖
    install_optional_dependencies()
    
    # 验证安装
    if not verify_installation():
        print("❌ 依赖验证失败")
        sys.exit(1)
    
    print("\n🎉 安装完成！")
    print("\n📚 可运行的示例文件:")
    print("   python learn/第一个langgraph学习.py")
    print("   python learn/节点函数设计.py")
    print("   python learn/自主代理.py")
    print("   python learn/多Agent协作.py")
    print("   python learn/工具调用.py")
    print("   python learn/智能客服.py")
    print("   python learn/UI集成.py")
    
    print("\n💡 重要提示:")
    print("   - 确保 Ollama 服务正在运行 (http://localhost:11434)")
    print("   - 或者配置 OpenAI API 密钥 (设置 OPENAI_API_KEY 环境变量)")
    print("   - 查看 README.md 了解更多使用说明")

if __name__ == "__main__":
    main()
