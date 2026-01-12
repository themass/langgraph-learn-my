#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Self-Reflection Prompt 模板配置
所有 prompt 模板都在这里定义，避免代码拼接，提高可读性
"""

import re


# =================================================================
# System Prompt
# =================================================================

SELF_REFLECTION_SYSTEM_PROMPT = """你是一个使用自我反思(Self-Reflection)方法解决问题的专家。

工作流程：
1. 生成初始答案
2. 反思和评估答案质量
3. 识别问题和不足
4. 改进答案
5. 重复直到达到质量标准

反思要点：
- 答案的完整性和准确性
- 逻辑的严密性
- 是否遗漏重要信息
- 是否可以更清晰、更详细
"""


# =================================================================
# Generate Answer Node Prompt Template
# =================================================================

SELF_REFLECTION_GENERATE_PROMPT_TEMPLATE = """问题：{question}

请直接回答这个问题，给出你的初始答案。

返回JSON格式：
{{"answer": "你的答案", "reasoning": "推理过程", "key_points": ["要点1", "要点2", ...]}}
"""


# =================================================================
# Reflect Node Prompt Template
# =================================================================

SELF_REFLECTION_REFLECT_PROMPT_TEMPLATE = """问题：{question}

当前答案：
{current_answer}

推理过程：
{reasoning}

请反思这个答案的质量，评估：
1. 答案是否完整？
2. 逻辑是否严密？
3. 是否有遗漏或错误？
4. 是否可以改进？

返回JSON格式：
{{"quality_score": 0-10的评分, "strengths": ["优点1", "优点2", ...], "weaknesses": ["缺点1", "缺点2", ...], "improvements": ["改进建议1", "改进建议2", ...], "is_sufficient": true/false 是否达到质量标准}}
"""


# =================================================================
# Improve Answer Node Prompt Template
# =================================================================

SELF_REFLECTION_IMPROVE_PROMPT_TEMPLATE = """问题：{question}

当前答案：
{current_answer}

反思结果：
- 优点：{strengths}
- 缺点：{weaknesses}
- 改进建议：{improvements}

请基于反思结果改进答案。返回JSON格式：
{{"improved_answer": "改进后的答案", "improvements_made": ["改进1", "改进2", ...], "reasoning": "改进的推理过程"}}
"""


# =================================================================
# Helper Functions
# =================================================================

def format_generate_prompt(question: str) -> str:
    """格式化生成答案节点 prompt"""
    prompt = SELF_REFLECTION_GENERATE_PROMPT_TEMPLATE.format(question=question)
    # 转义 JSON 示例中的花括号
    json_pattern = r'(\{[^}]*\})'
    def escape_braces(match):
        json_str = match.group(1)
        escaped = json_str.replace('{', '{{').replace('}', '}}')
        return escaped
    prompt = re.sub(json_pattern, escape_braces, prompt)
    return prompt


def format_reflect_prompt(question: str, current_answer: str, reasoning: str) -> str:
    """格式化反思节点 prompt"""
    prompt = SELF_REFLECTION_REFLECT_PROMPT_TEMPLATE.format(
        question=question,
        current_answer=current_answer,
        reasoning=reasoning
    )
    # 转义 JSON 示例中的花括号
    json_pattern = r'(\{[^}]*\})'
    def escape_braces(match):
        json_str = match.group(1)
        escaped = json_str.replace('{', '{{').replace('}', '}}')
        return escaped
    prompt = re.sub(json_pattern, escape_braces, prompt)
    return prompt


def format_improve_prompt(
    question: str,
    current_answer: str,
    strengths: str,
    weaknesses: str,
    improvements: str
) -> str:
    """格式化改进答案节点 prompt"""
    prompt = SELF_REFLECTION_IMPROVE_PROMPT_TEMPLATE.format(
        question=question,
        current_answer=current_answer,
        strengths=strengths,
        weaknesses=weaknesses,
        improvements=improvements
    )
    # 转义 JSON 示例中的花括号
    json_pattern = r'(\{[^}]*\})'
    def escape_braces(match):
        json_str = match.group(1)
        escaped = json_str.replace('{', '{{').replace('}', '}}')
        return escaped
    prompt = re.sub(json_pattern, escape_braces, prompt)
    return prompt
