from typing import Dict
from agent_proj.graph.state import AgentState
from agent_proj.utils import get_llm
import re

def input_validation_node(state: AgentState) -> Dict:
    """
    Input Validation Node: 验证用户输入的合法性和合理性
    
    验证项：
    1. Topic 格式和长度
    2. 敏感词过滤
    3. 问题分类（简单/复杂）
    """
    topic = state.get("topic", "")
    
    # 1. 基本格式验证
    if not topic or len(topic.strip()) == 0:
        return {
            "error_state": "输入为空",
            "next_node": "end"
        }
    
    if len(topic) > 500:
        return {
            "error_state": "输入过长（超过500字符）",
            "next_node": "end"
        }
    
    # 2. 敏感词过滤（简化版，生产环境需要更完善的词库）
    sensitive_words = ["暴力", "色情", "赌博", "毒品"]
    for word in sensitive_words:
        if word in topic:
            return {
                "error_state": f"包含敏感词: {word}",
                "next_node": "end"
            }
    
    # 3. 问题分类（简单/复杂）
    # 简单问题：少于10个字，且没有"分析"、"研究"等关键词
    is_simple = len(topic) < 30 and not any(
        keyword in topic for keyword in ["分析", "研究", "评估", "对比", "深入"]
    )
    
    return {
        "input_validated": True,
        "is_simple_question": is_simple
    }
