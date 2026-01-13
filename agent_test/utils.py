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
    
    Args:
        temperature: 温度参数，控制随机性，默认 0.2
        model_name: 模型端点 ID，默认 ep-20240527113904-mrr8p
    
    Returns:
        ChatOpenAI 实例（配置为使用豆包 API）
    """
    # 豆包 AI 配置
    api_key = "e8995123-8a55-4529-ae57-cd3f5fbd5eaf"
    base_url = "https://ark.cn-beijing.volces.com/api/v3/"
    
    if temperature is None:
        temperature = 0.2
    
    if model_name is None:
        model_name = "ep-20240527113904-mrr8p"
    
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        api_key=api_key,
        base_url=base_url,
        model_kwargs={"top_p": 0.9}
    )
