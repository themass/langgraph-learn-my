#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Chain-of-Thought (CoT) Prompt 模板配置
所有 prompt 模板都在这里定义，避免代码拼接，提高可读性
"""

import re

# =================================================================
# System Prompt
# =================================================================

COT_SYSTEM_PROMPT = """你是一位擅长逐步推理的专家。你需要通过思维链(Chain-of-Thought)的方式解决复杂问题。

推理原则：
1. 将复杂问题分解为多个简单的子步骤
2. 每一步都要明确说明推理依据
3. 逐步推进，确保逻辑严密
4. 最终得出明确的结论

重要约束：
- 推理步骤限制：最多进行3步推理（不包括初始分析和最终结论）
- 你需要在有限的步骤内完成推理，每一步都要高效推进
- 如果当前步骤是最后一步，必须确保能够得出最终答案

推理格式：
步骤1: [分析问题]
- 关键信息：[提取的关键信息]
- 推理依据：[为什么这样分析]

步骤2: [进一步推理]
- 关键信息：[提取的关键信息]
- 推理依据：[为什么这样推理]

步骤N: [得出结论]
- 最终答案：[明确的结论]
- 推理依据：[总结推理过程]
"""


# =================================================================
# Analyze Node Prompt Template
# =================================================================

COT_ANALYZE_PROMPT_TEMPLATE = """请分析以下问题，提取关键信息：

问题：{question}

请返回JSON格式：
{{"key_elements": ["关键要素1", "关键要素2", ...], "constraints": ["约束条件1", "约束条件2", ...], "analysis": "对问题的初步分析"}}
"""


# =================================================================
# Reasoning Node Prompt Template
# =================================================================

COT_REASONING_PROMPT_TEMPLATE = """基于以下问题和你已有的推理步骤，继续下一步推理：

问题：{question}

已有推理步骤：
{context}

当前推理进度：
- 当前步骤：第 {current_step} 步（共 {max_steps} 步）
- 剩余步骤：{remaining_steps} 步
- {step_warning}

请进行下一步推理，返回JSON格式：
{{"step_name": "推理步骤名称", "content": "这一步的推理内容", "reasoning": "推理依据", "next_action": "下一步应该做什么", "can_conclude": false}}

注意：
- {step_note}
- 如果当前推理已经足够完整，可以得出最终答案，请设置 "can_conclude": true，表示可以提前结束推理
- "next_action" 可以是 "继续推理"、"得出最终答案" 等
"""


# =================================================================
# Conclude Node Prompt Template
# =================================================================

COT_CONCLUDE_PROMPT_TEMPLATE = """基于以下问题和完整的推理过程，得出最终答案：

问题：{question}

完整推理过程：
{context}

请返回JSON格式：
{{"final_answer": "明确的最终答案", "summary": "推理过程总结", "confidence": "对答案的信心程度（高/中/低）"}}
"""


# =================================================================
# Helper Functions
# =================================================================

def get_step_warning(is_last_step: bool) -> str:
    """获取步骤警告信息"""
    if is_last_step:
        return "⚠️ 这是最后一步推理，必须确保能够得出最终答案或接近最终答案"
    return "✓ 还有后续推理步骤"


def get_step_note(is_last_step: bool) -> str:
    """获取步骤提示信息"""
    if is_last_step:
        return "这是最后一步推理，请确保推理完整，能够得出最终答案。"
    return "请高效推进推理，为后续步骤做好准备。"


def format_analyze_prompt(question: str) -> str:
    """格式化分析节点 prompt"""
    prompt = COT_ANALYZE_PROMPT_TEMPLATE.format(question=question)
    # 转义 JSON 示例中的所有花括号，避免 LangChain 误认为是变量
    # 匹配 JSON 示例部分（从 {" 开始到 } 结束）
    json_pattern = r'(\{[^}]*\})'
    def escape_braces(match):
        json_str = match.group(1)
        # 将单个花括号转义为双花括号
        escaped = json_str.replace('{', '{{').replace('}', '}}')
        return escaped
    prompt = re.sub(json_pattern, escape_braces, prompt)
    return prompt


def format_reasoning_prompt(
    question: str,
    context: str,
    current_step: int,
    max_steps: int,
    remaining_steps: int,
    is_last_step: bool
) -> str:
    """格式化推理节点 prompt"""
    step_warning = get_step_warning(is_last_step)
    step_note = get_step_note(is_last_step)
    
    prompt = COT_REASONING_PROMPT_TEMPLATE.format(
        question=question,
        context=context,
        current_step=current_step,
        max_steps=max_steps,
        remaining_steps=remaining_steps,
        step_warning=step_warning,
        step_note=step_note
    )
    # 转义 JSON 示例中的所有花括号，避免 LangChain 误认为是变量
    json_pattern = r'(\{[^}]*\})'
    def escape_braces(match):
        json_str = match.group(1)
        escaped = json_str.replace('{', '{{').replace('}', '}}')
        return escaped
    prompt = re.sub(json_pattern, escape_braces, prompt)
    return prompt


def format_conclude_prompt(question: str, context: str) -> str:
    """格式化结论节点 prompt"""
    prompt = COT_CONCLUDE_PROMPT_TEMPLATE.format(
        question=question,
        context=context
    )
    # 转义 JSON 示例中的所有花括号，避免 LangChain 误认为是变量
    json_pattern = r'(\{[^}]*\})'
    def escape_braces(match):
        json_str = match.group(1)
        escaped = json_str.replace('{', '{{').replace('}', '}}')
        return escaped
    prompt = re.sub(json_pattern, escape_braces, prompt)
    return prompt
