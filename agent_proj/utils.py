#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utilities for Model Factory and Configuration.
"""

from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from pathlib import Path

# 加载项目根目录的 .env 文件
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

def get_llm(temperature=None, model_name=None):
    """
    Factory to get ChatOpenAI instance.
    Supports OpenAI, Moonshot, or compatible APIs via base_url.
    Default to Moonshot (Kimi) as configured in .env
    
    Args:
        temperature: LLM 温度参数 (0-1)，默认从 .env 读取
        model_name: LLM 模型名称，默认从 .env 读取
        
    Returns:
        ChatOpenAI 实例
        
    Raises:
        ValueError: 如果未配置 API Key
    """
    # 1. 从环境变量获取 API Key
    api_key = os.environ.get("MOONSHOT_API_KEY") or os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError(
            "未找到 LLM API Key！\n"
            "请在项目根目录的 .env 文件中配置:\n"
            "  MOONSHOT_API_KEY=your_api_key_here\n"
            "或\n"
            "  OPENAI_API_KEY=your_api_key_here\n"
            "\n"
            "如果没有 .env 文件，请复制 .env.example:\n"
            "  cp .env.example .env"
        )
    
    # 2. 从环境变量获取 Base URL
    base_url = (
        os.environ.get("MOONSHOT_BASE_URL") or 
        os.environ.get("OPENAI_BASE_URL") or 
        "https://api.moonshot.cn/v1"
    )
    
    # 3. 从环境变量获取默认配置（如果参数未指定）
    if temperature is None:
        temperature = float(os.environ.get("DEFAULT_LLM_TEMPERATURE", "0.3"))
    
    if model_name is None:
        model_name = os.environ.get("DEFAULT_LLM_MODEL", "moonshot-v1-32k")
    
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        api_key=api_key,
        base_url=base_url
    )
