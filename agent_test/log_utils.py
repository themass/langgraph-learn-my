#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志工具函数
"""

import json
import logging
from typing import Any, Dict, List, Union
from langchain_core.messages import BaseMessage

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def log_node_input(node_name: str, state: Dict[str, Any]):
    """记录节点输入"""
    logger = logging.getLogger(node_name)
    logger.info("=" * 60)
    logger.info(f"【节点】{node_name} - 开始执行")
    logger.info(f"【输入】state: {json.dumps(state, ensure_ascii=False, indent=2, default=str)}")


def log_prompt(node_name: str, prompt_messages: Union[List[BaseMessage], List[tuple], Any]):
    """记录发送给 LLM 的完整 prompt"""
    logger = logging.getLogger(node_name)
    
    try:
        # 构建完整的 prompt 字符串
        prompt_lines = ["【Prompt】发送给 LLM 的完整内容："]
        
        # 如果是 ChatPromptTemplate 的 messages 格式 (list of tuples)
        if isinstance(prompt_messages, list) and len(prompt_messages) > 0:
            if isinstance(prompt_messages[0], tuple):
                # 格式: [("system", "..."), ("human", "...")]
                for role, content in prompt_messages:
                    prompt_lines.append(f"  [{role.upper()}]:")
                    # 将多行内容按行分割，每行前加缩进
                    content_lines = str(content).split('\n')
                    for line in content_lines:
                        prompt_lines.append(f"  {line}")
            elif hasattr(prompt_messages[0], 'content'):
                # 格式: [SystemMessage(...), HumanMessage(...)]
                for msg in prompt_messages:
                    role = type(msg).__name__.replace('Message', '').lower()
                    prompt_lines.append(f"  [{role.upper()}]:")
                    content_lines = str(msg.content).split('\n')
                    for line in content_lines:
                        prompt_lines.append(f"  {line}")
            else:
                prompt_lines.append(f"  {json.dumps(prompt_messages, ensure_ascii=False, indent=2, default=str)}")
        else:
            content_lines = str(prompt_messages).split('\n')
            for line in content_lines:
                prompt_lines.append(f"  {line}")
        
        # 将所有内容合并为一条日志记录，避免每行都打印时间戳
        logger.info('\n'.join(prompt_lines))
    except Exception as e:
        logger.warning(f"  无法格式化 prompt: {e}")
        logger.info(f"  {str(prompt_messages)}")


def log_node_output(node_name: str, output: Dict[str, Any]):
    """记录节点输出"""
    logger = logging.getLogger(node_name)
    logger.info(f"【输出】output: {json.dumps(output, ensure_ascii=False, indent=2, default=str)}")
    logger.info(f"【节点】{node_name} - 执行完成")
    logger.info("=" * 60)
