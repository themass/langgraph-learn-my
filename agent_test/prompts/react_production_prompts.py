#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ReAct (Reasoning + Acting) 生产级 Prompt 模板配置
所有 prompt 模板都在这里定义，避免代码拼接，提高可读性
"""

import re


# =================================================================
# System Prompt
# =================================================================

REACT_PRODUCTION_SYSTEM_PROMPT = """你是一位专业的智能代理，使用 ReAct (Reasoning + Acting) 模式解决复杂问题。

核心能力：
1. 理性思考 - 基于知识和观察进行逻辑推理
2. 工具使用 - 选择并使用合适的工具获取信息
3. 自我反思 - 评估行动效果，调整策略
4. 持续学习 - 从观察中学习，优化决策

工作原则：
- 每一步都要有明确的推理依据
- 选择最有效的工具完成任务
- 持续评估进展，必要时调整策略
- 最终给出可靠、可执行的解决方案

输出要求：
- 所有回复必须是有效的 JSON 格式
- 思考过程要详细但简洁
- 选择行动要有充分理由
"""


# =================================================================
# 1. Task Analysis Node Prompts
# =================================================================

REACT_TASK_ANALYSIS_PROMPT_TEMPLATE = """分析以下任务，提取关键信息：

任务：{task}

请分析：
1. 任务领域（医学/法律/计算机/通用等）
2. 任务类型（信息检索/计算/决策/创作等）
3. 关键实体和概念
4. 任务约束条件
5. 任务复杂度（simple/medium/complex）
6. 预估需要的工具类型

返回JSON格式：
{{{{
  "domain": "任务领域",
  "task_type": "任务类型",
  "key_entities": ["关键实体1", "关键实体2"],
  "constraints": ["约束1", "约束2"],
  "complexity": "simple|medium|complex",
  "required_tools": ["工具1", "工具2"]
}}}}
"""


# =================================================================
# 2. Knowledge Preparation Node Prompts
# =================================================================

REACT_KNOWLEDGE_PREP_PROMPT_TEMPLATE = """基于任务分析，准备必要的知识：

任务：{task}
领域：{domain}
关键实体：{key_entities}

已检索的知识：
{retrieved_knowledge}

请评估：
1. 当前知识是否充分？
2. 还需要什么额外信息？
3. 知识的可信度如何？
4. 是否需要进一步检索？

返回JSON格式：
{{{{
  "knowledge_sufficient": true/false,
  "missing_info": ["缺失的信息1", "缺失的信息2"],
  "knowledge_confidence": 0.0-1.0,
  "need_more_retrieval": true/false,
  "retrieval_queries": ["新检索查询1", "新检索查询2"]
}}}}
"""


# =================================================================
# 3. Think Node Prompts
# =================================================================

REACT_THINK_PROMPT_TEMPLATE = """【思考阶段】

任务：{task}

当前情况：
- 执行轮次：第 {iteration} 轮（最多 {max_iterations} 轮）
- 当前观察：{observation}

可用知识：
{knowledge_summary}

执行历史：
{history_summary}

可用工具：
{tools_description}

当前策略：{current_strategy}

请深入思考：
1. 当前任务的完成进度如何？
2. 最近的观察告诉了我什么？
3. 下一步应该采取什么行动？
   - 如果需要更多信息 → 使用工具
   - 如果需要计算 → 使用计算工具
   - 如果信息充足 → 选择 finish
4. 为什么这个行动是最优的？

返回JSON格式：
{{{{
  "thought": "详细的思考过程",
  "current_progress": "当前进展评估",
  "action": "工具名称或finish",
  "action_input": "行动参数（JSON格式）",
  "reasoning": "选择这个行动的理由",
  "confidence": 0.0-1.0
}}}}
"""


# =================================================================
# 4. Observe & Reflect Node Prompts
# =================================================================

REACT_OBSERVE_REFLECT_PROMPT_TEMPLATE = """【观察与反思阶段】

刚刚执行的行动：
- 行动：{action}
- 参数：{action_input}
- 结果：{observation}
- 执行状态：{tool_success}

当前策略：{current_strategy}

执行历史：
{history_summary}

请反思：
1. 这个行动是否达到了预期效果？
2. 从观察结果中学到了什么？
3. 当前策略是否有效？
4. 是否需要调整策略或方向？
5. 对完成任务的信心程度如何？
6. 是否应该继续还是准备得出结论？

返回JSON格式：
{{{{
  "reflection": "对行动结果的反思",
  "action_effective": true/false,
  "learned_info": ["学到的信息1", "学到的信息2"],
  "strategy_effective": true/false,
  "need_strategy_change": true/false,
  "suggested_strategy": "建议的新策略（如需调整）",
  "confidence_score": 0.0-1.0,
  "should_continue": true/false,
  "reasoning": "是否继续的理由"
}}}}
"""


# =================================================================
# 5. Answer Generation Node Prompts
# =================================================================

REACT_ANSWER_GENERATION_PROMPT_TEMPLATE = """【答案生成阶段】

任务：{task}

完整执行历史：
{complete_history}

相关知识：
{knowledge_summary}

工具调用记录：
{tool_calls_summary}

请生成最终答案：
1. 明确、准确的最终答案
2. 详细的解释（基于执行历史）
3. 实施步骤（如果任务需要执行）
4. 替代方案（如果有）
5. 局限性说明（答案的不确定性和前提条件）

返回JSON格式：
{{{{
  "final_answer": "清晰、准确的最终答案",
  "explanation": "详细解释（为什么这是答案）",
  "implementation_steps": ["步骤1", "步骤2", "..."],
  "alternative_solutions": ["替代方案1", "替代方案2"],
  "limitations": "局限性说明",
  "confidence": 0.0-1.0
}}}}
"""


# =================================================================
# 6. Quality Assessment Node Prompts
# =================================================================

REACT_QUALITY_ASSESSMENT_PROMPT_TEMPLATE = """【质量评估阶段】

任务：{task}

生成的答案：
{final_answer}

答案解释：
{explanation}

执行历史：
{history_summary}

置信度：{confidence}

请评估答案质量：
1. 完整性：答案是否完整回答了问题？
2. 准确性：答案是否基于可靠的信息和推理？
3. 清晰度：答案是否清晰易懂？
4. 可执行性：答案是否可操作、可验证？
5. 总体质量评分（0-10）

返回JSON格式：
{{{{
  "quality_score": 0-10,
  "completeness_score": 0-10,
  "accuracy_score": 0-10,
  "clarity_score": 0-10,
  "actionability_score": 0-10,
  "strengths": ["优点1", "优点2"],
  "weaknesses": ["缺点1", "缺点2"],
  "needs_retry": true/false,
  "retry_suggestions": ["改进建议1", "改进建议2"],
  "assessment_summary": "总体评估"
}}}}
"""


# =================================================================
# Helper Functions - Prompt Formatting
# =================================================================

def _escape_json_in_template(template: str) -> str:
    """转义模板中 JSON 示例的花括号"""
    # 查找所有 JSON 示例块（在 {{{{ }}}} 之间）
    pattern = r'\{\{\{\{(.*?)\}\}\}\}'
    
    def replace_braces(match):
        content = match.group(1)
        # 将内部的 { } 替换为 {{{{ }}}}
        escaped = content.replace('{', '{{{{').replace('}', '}}}}')
        return '{{{{' + escaped + '}}}}'
    
    return re.sub(pattern, replace_braces, template, flags=re.DOTALL)


def format_task_analysis_prompt(task: str) -> str:
    """格式化任务分析 prompt"""
    return REACT_TASK_ANALYSIS_PROMPT_TEMPLATE.format(task=task)


def format_knowledge_prep_prompt(
    task: str,
    domain: str,
    key_entities: str,
    retrieved_knowledge: str
) -> str:
    """格式化知识准备 prompt"""
    return REACT_KNOWLEDGE_PREP_PROMPT_TEMPLATE.format(
        task=task,
        domain=domain,
        key_entities=key_entities,
        retrieved_knowledge=retrieved_knowledge
    )


def format_think_prompt(
    task: str,
    iteration: int,
    max_iterations: int,
    observation: str,
    knowledge_summary: str,
    history_summary: str,
    tools_description: str,
    current_strategy: str
) -> str:
    """格式化思考 prompt"""
    return REACT_THINK_PROMPT_TEMPLATE.format(
        task=task,
        iteration=iteration,
        max_iterations=max_iterations,
        observation=observation,
        knowledge_summary=knowledge_summary,
        history_summary=history_summary,
        tools_description=tools_description,
        current_strategy=current_strategy
    )


def format_observe_reflect_prompt(
    action: str,
    action_input: str,
    observation: str,
    tool_success: bool,
    current_strategy: str,
    history_summary: str
) -> str:
    """格式化观察与反思 prompt"""
    return REACT_OBSERVE_REFLECT_PROMPT_TEMPLATE.format(
        action=action,
        action_input=action_input,
        observation=observation,
        tool_success="成功" if tool_success else "失败",
        current_strategy=current_strategy,
        history_summary=history_summary
    )


def format_answer_generation_prompt(
    task: str,
    complete_history: str,
    knowledge_summary: str,
    tool_calls_summary: str
) -> str:
    """格式化答案生成 prompt"""
    return REACT_ANSWER_GENERATION_PROMPT_TEMPLATE.format(
        task=task,
        complete_history=complete_history,
        knowledge_summary=knowledge_summary,
        tool_calls_summary=tool_calls_summary
    )


def format_quality_assessment_prompt(
    task: str,
    final_answer: str,
    explanation: str,
    history_summary: str,
    confidence: float
) -> str:
    """格式化质量评估 prompt"""
    return REACT_QUALITY_ASSESSMENT_PROMPT_TEMPLATE.format(
        task=task,
        final_answer=final_answer,
        explanation=explanation,
        history_summary=history_summary,
        confidence=confidence
    )
