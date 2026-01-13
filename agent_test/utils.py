#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
工具函数：统一的 LLM 模型配置
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
    获取豆包 AI (DoubaoAI) 模型实例
    从 .env 文件读取配置
    
    Args:
        temperature: 温度参数，控制随机性，默认从 .env 读取
        model_name: 模型端点 ID，默认从 .env 读取
    
    Returns:
        ChatOpenAI 实例（配置为使用豆包 API）
        
    Raises:
        ValueError: 如果未配置 API Key
    """
    # 从环境变量读取配置
    api_key = os.environ.get("DOUBAO_API_KEY")
    base_url = os.environ.get("DOUBAO_BASE_URL")
    
    if not api_key:
        raise ValueError(
            "未找到豆包 AI 的 API Key！\n"
            "请在项目根目录的 .env 文件中配置:\n"
            "  DOUBAO_API_KEY=your_api_key_here\n"
            "  DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3/\n"
            "  DOUBAO_MODEL=your_model_endpoint_id\n"
        )
    
    if not base_url:
        base_url = "https://ark.cn-beijing.volces.com/api/v3/"
    
    if temperature is None:
        temperature = float(os.environ.get("DOUBAO_TEMPERATURE", "0.2"))
    
    if model_name is None:
        model_name = os.environ.get("DOUBAO_MODEL", "ep-20240527113904-mrr8p")
    
    top_p = float(os.environ.get("DOUBAO_TOP_P", "0.9"))
    
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        api_key=api_key,
        base_url=base_url,
        model_kwargs={"top_p": top_p}
    )
