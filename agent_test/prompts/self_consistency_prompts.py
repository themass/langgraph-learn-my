#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Self-Consistency Prompt 模板配置
所有 prompt 模板都在这里定义，避免代码拼接，提高可读性
"""

import re


# =================================================================
# System Prompt
# =================================================================

SELF_CONSISTENCY_SYSTEM_PROMPT = """你是一个使用自我一致性(Self-Consistency)方法解决问题的专家。

工作流程：
1. 对同一个问题生成多个独立的推理路径
2. 每个路径都应该独立推理，不受其他路径影响
3. 最终通过一致性评估选择最可靠的答案

推理要求：
- 每个推理路径都应该完整、独立
- 推理过程要清晰、逻辑严密
- 最终答案要明确
"""


# =================================================================
# Generate Reasoning Path Node Prompt Template
# =================================================================

SELF_CONSISTENCY_GENERATE_PROMPT_TEMPLATE = """问题：{question}

请独立地、完整地推理这个问题，给出你的答案。

推理过程：
1. 分析问题的关键要素
2. 逐步推理
3. 得出明确结论

返回JSON格式：
{{"reasoning": "完整的推理过程", "answer": "明确的答案", "confidence": "信心程度（高/中/低）", "key_points": ["关键点1", "关键点2", ...]}}
"""


# =================================================================
# Evaluate Consistency Node Prompt Template
# =================================================================

SELF_CONSISTENCY_EVALUATE_PROMPT_TEMPLATE = """以下是同一个问题的多个答案：

{answers_text}

请评估这些答案的一致性，并选择最可靠的答案。返回JSON格式：
{{"most_common_answer": "出现次数最多的答案", "consistency_score": 0-1的一致性分数, "reasoning": "评估理由", "final_answer": "最终选择的答案"}}
"""


# =================================================================
# Helper Functions
# =================================================================

def format_generate_prompt(question: str) -> str:
    """格式化生成推理路径节点 prompt"""
    prompt = SELF_CONSISTENCY_GENERATE_PROMPT_TEMPLATE.format(question=question)
    # 转义 JSON 示例中的花括号
    json_pattern = r'(\{[^}]*\})'
    def escape_braces(match):
        json_str = match.group(1)
        escaped = json_str.replace('{', '{{').replace('}', '}}')
        return escaped
    prompt = re.sub(json_pattern, escape_braces, prompt)
    return prompt


def format_evaluate_prompt(answers_text: str) -> str:
    """格式化评估一致性节点 prompt"""
    prompt = SELF_CONSISTENCY_EVALUATE_PROMPT_TEMPLATE.format(answers_text=answers_text)
    # 转义 JSON 示例中的花括号
    json_pattern = r'(\{[^}]*\})'
    def escape_braces(match):
        json_str = match.group(1)
        escaped = json_str.replace('{', '{{').replace('}', '}}')
        return escaped
    prompt = re.sub(json_pattern, escape_braces, prompt)
    return prompt
