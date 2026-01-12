#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Chain-of-Thought (CoT) 生产级 Prompt 模板配置
所有 prompt 模板都在这里定义，避免代码拼接，提高可读性
"""

import re


# =================================================================
# System Prompt
# =================================================================

COT_PRODUCTION_SYSTEM_PROMPT = """你是一位专业的领域专家，擅长通过思维链(Chain-of-Thought)的方式解决复杂问题。

推理原则：
1. 将复杂问题分解为多个简单的子步骤
2. 每一步都要明确说明推理依据
3. 基于提供的领域知识进行推理
4. 逐步推进，确保逻辑严密
5. 最终得出明确的结论

重要约束：
- 推理步骤限制：最多进行3步推理（不包括初始分析和最终结论）
- 你需要在有限的步骤内完成推理，每一步都要高效推进
- 如果当前步骤是最后一步，必须确保能够得出最终答案
- 充分利用提供的领域知识，确保推理的专业性和准确性

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
# Prompt 模板定义
# =================================================================

# 信息收集节点 Prompt 模板
GATHER_INFO_PROMPT_TEMPLATE = """请分析以下问题，确定解决问题所需的关键信息：

问题：{question}
领域：{domain}
上下文信息：{context}

请考虑以下方面：
1. 问题的核心是什么
2. 问题属于哪个领域或子领域
3. 解决此类问题通常需要哪些关键信息
4. 问题中可能存在哪些隐含条件或假设

请返回JSON格式：
{{"required_info": ["所需信息1", "所需信息2", ...], "problem_classification": "问题分类", "complexity": 复杂度评估(1-10)}}
"""

# 知识检索节点 Prompt 模板
QUERY_KNOWLEDGE_PROMPT_TEMPLATE = """请评估以下知识条目与问题的相关性：

问题：{question}
领域：{domain}
所需信息：{required_info}

知识条目：
{knowledge_text}

请对每个知识条目进行评估，返回JSON格式：
{{{{"relevant_entries": [{{{{"id": "知识ID", "relevance_score": 0-10的评分, "relevance_explanation": "评分理由"}}}}], "按相关性降序排列"}}}}
"""

# 分析节点 Prompt 模板
ANALYZE_PROMPT_TEMPLATE = """请分析以下问题，提取关键信息：

问题：{question}
领域：{domain}

相关知识：
{knowledge}

请返回JSON格式：
{{{{"key_elements": ["关键要素1", "关键要素2", ...], "constraints": ["约束条件1", "约束条件2", ...], "analysis": "对问题的初步分析"}}}}
"""

# 推理节点 Prompt 模板（基础部分）
REASONING_PROMPT_TEMPLATE_BASE = """基于以下问题、已有推理步骤和相关知识，继续下一步推理：

问题：{question}

已有推理步骤：
{context}

相关知识：
{knowledge}

当前推理进度：
- 当前步骤：第 {current_step} 步（共 {max_steps} 步）
- 剩余步骤：{remaining_steps} 步
- {step_warning}

请进行下一步推理，返回JSON格式：
{json_template}

注意：
- {step_note}
- 如果当前推理已经足够完整，可以得出最终答案，请设置 "can_conclude": true，表示可以提前结束推理
- "next_action" 可以是 "继续推理"、"得出最终答案" 等
- 充分利用提供的领域知识，确保推理的专业性{alternative_paths_note}
"""

# 结论节点 Prompt 模板
CONCLUDE_PROMPT_TEMPLATE = """基于以下问题和完整的推理过程，得出最终答案：

问题：{question}

完整推理过程：
{context}

相关知识：
{knowledge}{alternative_paths_section}

请返回JSON格式：
{{{{"final_answer": "明确的最终答案", "summary": "推理过程总结", "confidence": "对答案的信心程度（高/中/低）", "explanation": "详细解释解决方案的原理和依据", "implementation_steps": ["实施步骤1", "实施步骤2", ...], "limitations": ["局限性1", "局限性2", ...]}}}}

注意：
- "implementation_steps" 应该提供清晰、可操作的实施步骤（如果问题需要实施）
- "limitations" 应该诚实地指出方案的局限性和风险
- "explanation" 应该包含专业的理论依据和知识支持
"""

# 不确定性评估 Prompt 模板
UNCERTAINTY_PROMPT_TEMPLATE = """请评估以下推理过程和解决方案中的不确定性：

推理步骤：
{reasoning}

解决方案：
{solution}

请提供不确定性分析，返回JSON格式：
{{{{"confidence_scores": {{{{"overall": 0-1的评分, "completeness": 0-1的评分, "consistency": 0-1的评分, "evidence_strength": 0-1的评分}}}}, "uncertainty_sources": ["不确定性来源1", ...], "recommendations": ["处理建议1", ...]}}}}
"""


# =================================================================
# 辅助函数：花括号转义
# =================================================================

def escape_json_braces(text: str) -> str:
    """
    转义文本中的花括号，避免 ChatPromptTemplate 误认为是变量
    
    Args:
        text: 需要转义的文本（通常是 JSON 字符串）
        
    Returns:
        转义后的文本
    """
    return text.replace('{', '{{').replace('}', '}}')


# =================================================================
# Prompt 格式化函数
# =================================================================

def format_gather_info_prompt(question: str, domain: str, context: str) -> str:
    """
    格式化信息收集 Prompt
    
    Args:
        question: 问题内容
        domain: 领域类别
        context: 上下文信息（JSON 字符串）
        
    Returns:
        格式化后的 prompt 字符串
    """
    # 转义 context 中的花括号
    escaped_context = escape_json_braces(context)
    
    # 格式化 prompt
    prompt = GATHER_INFO_PROMPT_TEMPLATE.format(
        question=question,
        domain=domain,
        context=escaped_context
    )
    
    # 转义 JSON 示例中的花括号
    prompt = re.sub(
        r'(\{[^}]*"required_info"[^}]*\})',
        lambda m: escape_json_braces(m.group(1)),
        prompt
    )
    
    return prompt


def format_query_knowledge_prompt(
    question: str,
    domain: str,
    required_info: str,
    knowledge_text: str
) -> str:
    """
    格式化知识检索 Prompt
    
    Args:
        question: 问题内容
        domain: 领域类别
        required_info: 所需信息（JSON 字符串）
        knowledge_text: 知识条目文本
        
    Returns:
        格式化后的 prompt 字符串
    """
    # 转义所有参数中的花括号（因为它们可能包含 JSON）
    escaped_required_info = escape_json_braces(required_info)
    escaped_knowledge_text = escape_json_braces(knowledge_text)
    
    # 格式化 prompt（模板中的 JSON 示例已经使用 {{{{ 转义）
    prompt = QUERY_KNOWLEDGE_PROMPT_TEMPLATE.format(
        question=question,
        domain=domain,
        required_info=escaped_required_info,
        knowledge_text=escaped_knowledge_text
    )
    
    return prompt


def format_analyze_prompt(question: str, domain: str, knowledge: str) -> str:
    """
    格式化分析节点 Prompt
    
    Args:
        question: 问题内容
        domain: 领域类别
        knowledge: 相关知识文本
        
    Returns:
        格式化后的 prompt 字符串
    """
    # 转义 knowledge 参数
    escaped_knowledge = escape_json_braces(knowledge)
    
    prompt = ANALYZE_PROMPT_TEMPLATE.format(
        question=question,
        domain=domain,
        knowledge=escaped_knowledge
    )
    
    return prompt


def format_reasoning_prompt(
    question: str,
    context: str,
    knowledge: str,
    current_step: int,
    max_steps: int,
    remaining_steps: int,
    is_last_step: bool
) -> str:
    """
    格式化推理节点 Prompt
    
    Args:
        question: 问题内容
        context: 已有推理步骤
        knowledge: 相关知识文本
        current_step: 当前步骤编号
        max_steps: 最大步骤数
        remaining_steps: 剩余步骤数
        is_last_step: 是否是最后一步
        
    Returns:
        格式化后的 prompt 字符串
    """
    # 准备步骤提示信息
    step_warning = (
        "⚠️ 这是最后一步推理，必须确保能够得出最终答案或接近最终答案"
        if is_last_step
        else "✓ 还有后续推理步骤"
    )
    step_note = (
        "这是最后一步推理，请确保推理完整，能够得出最终答案。"
        if is_last_step
        else "请高效推进推理，为后续步骤做好准备。"
    )
    
    # 准备替代路径提示
    alternative_paths_note = ""
    if is_last_step:
        alternative_paths_note = """
- 请考虑是否有其他可能的推理路径或解决方案（alternative_paths），即使当前路径看起来合理
- 如果存在替代路径，简要说明其优缺点"""
    
    # 构建 JSON 格式字符串（普通字符串，不转义）
    if is_last_step:
        json_template = (
            '{"step_name": "推理步骤名称", "content": "这一步的推理内容", '
            '"reasoning": "推理依据", "next_action": "下一步应该做什么", "can_conclude": false, '
            '"alternative_paths": [{"description": "替代路径描述", "reasoning": "为什么考虑这个路径", '
            '"pros": "优点", "cons": "缺点"}]}' 
        )
    else:
        json_template = (
            '{"step_name": "推理步骤名称", "content": "这一步的推理内容", '
            '"reasoning": "推理依据", "next_action": "下一步应该做什么", "can_conclude": false}'
        )
    
    # 转义 json_template 以便在 .format() 中使用
    escaped_json_template = escape_json_braces(json_template)
    
    # 格式化 prompt
    prompt = REASONING_PROMPT_TEMPLATE_BASE.format(
        question=question,
        context=context,
        knowledge=knowledge,
        current_step=current_step,
        max_steps=max_steps,
        remaining_steps=remaining_steps,
        step_warning=step_warning,
        step_note=step_note,
        json_template=escaped_json_template,  # 使用转义后的 JSON
        alternative_paths_note=alternative_paths_note
    )
    
    return prompt


def format_conclude_prompt(
    question: str,
    context: str,
    knowledge: str,
    alternative_paths: str = ""
) -> str:
    """
    格式化结论节点 Prompt
    
    Args:
        question: 问题内容
        context: 完整推理过程
        knowledge: 相关知识文本
        alternative_paths: 替代推理路径文本（可选）
        
    Returns:
        格式化后的 prompt 字符串
    """
    # 转义所有可能包含 JSON 的参数
    escaped_context = escape_json_braces(context)
    escaped_knowledge = escape_json_braces(knowledge)
    escaped_alternative_paths = escape_json_braces(alternative_paths)
    
    # 准备替代路径部分
    alternative_paths_section = ""
    if alternative_paths:
        alternative_paths_section = f"""

替代推理路径：
{escaped_alternative_paths}
"""
    
    # 格式化 prompt
    prompt = CONCLUDE_PROMPT_TEMPLATE.format(
        question=question,
        context=escaped_context,
        knowledge=escaped_knowledge,
        alternative_paths_section=alternative_paths_section
    )
    
    return prompt


def format_uncertainty_prompt(reasoning: str, solution: str) -> str:
    """
    格式化不确定性评估 Prompt
    
    Args:
        reasoning: 推理步骤文本
        solution: 解决方案文本（JSON 字符串）
        
    Returns:
        格式化后的 prompt 字符串
    """
    # 转义参数
    escaped_reasoning = escape_json_braces(reasoning)
    escaped_solution = escape_json_braces(solution)
    
    prompt = UNCERTAINTY_PROMPT_TEMPLATE.format(
        reasoning=escaped_reasoning,
        solution=escaped_solution
    )
    
    return prompt
