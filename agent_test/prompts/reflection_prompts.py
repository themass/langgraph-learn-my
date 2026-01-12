#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
反思模块 Prompt 模板配置
用于 CoT 和 ReAct 模式的反思功能
"""

import re


# =================================================================
# CoT 反思 Prompt
# =================================================================

COT_REFLECTION_SYSTEM_PROMPT = """你是一位专业的推理质量评估专家，擅长评估推理过程的质量和可靠性。

评估要点：
1. 推理逻辑是否严密？
2. 是否有遗漏的关键信息？
3. 推理步骤是否连贯？
4. 是否达到当前步骤的目标？
5. 推理依据是否充分？

请客观、专业地评估推理质量，并提供改进建议。"""


COT_REFLECTION_PROMPT_TEMPLATE = """请评估以下推理步骤的质量：

问题：{question}

当前推理步骤：
{reasoning_steps}

当前步骤：第 {current_step} 步（共 {max_steps} 步）

请评估：
1. 推理逻辑是否严密？
2. 是否有遗漏的关键信息？
3. 推理步骤是否连贯？
4. 是否达到当前步骤的目标？
5. 推理依据是否充分？

返回JSON格式：
{{"quality_score": 0-10的评分, "issues": ["问题1", "问题2", ...], "strengths": ["优点1", "优点2", ...], "needs_improvement": true/false, "improvement_suggestions": ["改进建议1", "改进建议2", ...]}}"""


def format_cot_reflection_prompt(
    question: str,
    reasoning_steps: str,
    current_step: int,
    max_steps: int
) -> str:
    """格式化 CoT 反思 Prompt"""
    prompt = COT_REFLECTION_PROMPT_TEMPLATE.format(
        question=question,
        reasoning_steps=reasoning_steps,
        current_step=current_step,
        max_steps=max_steps
    )
    # 转义 JSON 示例中的花括号
    prompt = re.sub(r'(\{[^}]*\})', lambda m: m.group(1).replace('{', '{{').replace('}', '}}'), prompt)
    return prompt


# =================================================================
# ReAct 反思 Prompt
# =================================================================

REACT_REFLECTION_SYSTEM_PROMPT = """你是一位专业的策略评估专家，擅长评估推理和行动的质量和有效性。

评估要点：
1. 思考过程是否合理？
2. 行动选择是否恰当？
3. 观察结果是否充分？
4. 整体策略是否需要调整？
5. 是否朝着目标前进？

请客观、专业地评估推理和行动的质量，并提供改进建议。"""


REACT_REFLECTION_PROMPT_TEMPLATE = """请反思以下推理和行动的质量：

问题：{question}

思考过程：
{thinking}

行动：
{action}

观察结果：
{observation}

当前迭代：第 {iteration} 次

请评估：
1. 思考过程是否合理？
2. 行动选择是否恰当？
3. 观察结果是否充分？
4. 整体策略是否需要调整？
5. 是否朝着目标前进？

返回JSON格式：
{{"quality_score": 0-10的评分, "strengths": ["优点1", "优点2", ...], "weaknesses": ["缺点1", "缺点2", ...], "suggestions": ["改进建议1", "改进建议2", ...], "needs_improvement": true/false, "strategy_adjustment": "策略调整建议"}}"""


def format_react_reflection_prompt(
    question: str,
    thinking: str,
    action: str,
    observation: str,
    iteration: int
) -> str:
    """格式化 ReAct 反思 Prompt"""
    prompt = REACT_REFLECTION_PROMPT_TEMPLATE.format(
        question=question,
        thinking=thinking,
        action=action,
        observation=observation,
        iteration=iteration
    )
    # 转义 JSON 示例中的花括号
    prompt = re.sub(r'(\{[^}]*\})', lambda m: m.group(1).replace('{', '{{').replace('}', '}}'), prompt)
    return prompt


# =================================================================
# 复杂度评估 Prompt（用于可选反思）
# =================================================================

COMPLEXITY_ASSESSMENT_SYSTEM_PROMPT = """你是一位专业的问题复杂度评估专家，擅长评估问题的复杂程度和是否需要深度反思。

评估因素：
1. 问题的长度和复杂度
2. 领域的专业性
3. 需要的信息量
4. 推理步骤的复杂度
5. 答案质量要求

请客观评估问题复杂度，并建议是否需要启用反思机制。"""


COMPLEXITY_ASSESSMENT_PROMPT_TEMPLATE = """请评估以下问题的复杂度：

问题：{question}
领域：{domain}
上下文：{context}

请评估：
1. 问题的长度和复杂度（1-10）
2. 领域的专业性（1-10）
3. 需要的信息量（1-10）
4. 推理步骤的复杂度（1-10）
5. 答案质量要求（1-10）

返回JSON格式：
{{"complexity_score": 0-10的综合评分, "factors": {{"length": 1-10, "domain": 1-10, "information": 1-10, "reasoning": 1-10, "quality": 1-10}}, "requires_reflection": true/false, "reason": "是否需要反思的原因"}}"""


def format_complexity_assessment_prompt(
    question: str,
    domain: str = "通用",
    context: str = ""
) -> str:
    """格式化复杂度评估 Prompt"""
    prompt = COMPLEXITY_ASSESSMENT_PROMPT_TEMPLATE.format(
        question=question,
        domain=domain,
        context=context
    )
    # 转义 JSON 示例中的花括号
    prompt = re.sub(r'(\{[^}]*\})', lambda m: m.group(1).replace('{', '{{').replace('}', '}}'), prompt)
    return prompt
