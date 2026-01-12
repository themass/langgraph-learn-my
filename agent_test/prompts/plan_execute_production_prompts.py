#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Plan-and-Execute 生产级 Prompt 模板配置
所有 prompt 模板都在这里定义，避免代码拼接，提高可读性
"""

import re


# =================================================================
# System Prompt
# =================================================================

PLAN_EXECUTE_PRODUCTION_SYSTEM_PROMPT = """你是一位专业的任务规划与执行专家，使用 Plan-and-Execute 策略高效解决复杂问题。

核心能力：
1. 战略规划 - 将复杂任务分解为清晰的执行步骤
2. 风险评估 - 识别潜在问题并制定应对策略
3. 灵活执行 - 根据实际情况调整执行方案
4. 质量保证 - 确保每步执行质量和整体目标达成

工作原则：
- 规划要全面但灵活，考虑多种可能性
- 执行要严格但不僵化，允许必要调整
- 评估要客观且及时，持续优化过程
- 结果要可靠且可验证，确保质量标准

输出要求：
- 所有回复必须是有效的 JSON 格式
- 规划要详细包含依赖关系和风险评估
- 执行要记录详细过程和中间结果
- 评估要给出明确的改进建议
"""


# =================================================================
# 1. Task Analysis & Planning Prompts
# =================================================================

TASK_ANALYSIS_PROMPT_TEMPLATE = """分析以下任务：

任务：{task}

请分析：
1. 任务类型（信息检索/计算/决策/创作等）
2. 任务复杂度（简单/中等/复杂）
3. 关键依赖（需要什么信息、工具、资源）
4. 潜在风险（可能遇到的问题）
5. 成功标准（如何判断任务完成）

返回JSON格式：
{{{{
  "task_type": "任务类型",
  "complexity": "simple|medium|complex",
  "key_dependencies": ["依赖1", "依赖2"],
  "potential_risks": ["风险1", "风险2"],
  "success_criteria": "成功标准描述",
  "estimated_steps": 数字
}}}}
"""


DETAILED_PLAN_PROMPT_TEMPLATE = """任务：{task}

任务分析：
{task_analysis}

可用工具：
{available_tools}

已检索的知识：
{knowledge_base}

请制定详细的执行计划。

规划要求：
1. 将任务分解为4-8个明确的步骤
2. 每个步骤包含：描述、类型、所需工具、依赖关系、风险评估
3. 步骤之间要有清晰的逻辑顺序
4. 考虑备选方案（如果主方案失败）
5. 估计每个步骤的复杂度和所需时间

返回JSON格式：
{{{{
  "plan": [
    {{{{
      "step_id": 1,
      "description": "详细描述",
      "action_type": "search|calculate|analyze|synthesize|tool_use",
      "required_tools": ["工具1"],
      "dependencies": [前置步骤ID],
      "estimated_complexity": "low|medium|high",
      "risk_level": "low|medium|high",
      "fallback_strategy": "备选策略",
      "expected_outcome": "预期结果"
    }}}}
  ],
  "overall_strategy": "整体策略说明",
  "critical_path": [关键路径步骤ID],
  "estimated_total_time": "预估总时间",
  "success_criteria": "整体成功标准"
}}}}
"""


REPLAN_PROMPT_TEMPLATE = """原始任务：{task}

原计划：
{original_plan}

已完成步骤及结果：
{completed_steps}

当前遇到的问题：
{issue}

失败原因分析：
{failure_analysis}

请重新规划剩余步骤。

重规划要求：
1. 保留有效的已完成步骤
2. 分析失败原因并调整策略
3. 设计新的步骤序列
4. 增加风险缓解措施
5. 提供更详细的执行指导

返回JSON格式：
{{{{
  "revised_plan": [新步骤列表],
  "changes_summary": "主要变更总结",
  "root_cause": "失败根本原因",
  "mitigation_strategies": ["缓解措施1", "措施2"],
  "confidence_level": 0.0-1.0,
  "alternative_approach": "备选方案说明"
}}}}
"""


# =================================================================
# 2. Execution Prompts
# =================================================================

EXECUTE_WITH_KNOWLEDGE_PROMPT_TEMPLATE = """当前步骤：
步骤ID：{step_id}
描述：{description}
类型：{action_type}
预期结果：{expected_outcome}

任务背景：
{task_context}

相关知识：
{relevant_knowledge}

已完成步骤的结果：
{previous_results}

可用工具：
{available_tools}

风险提示：
{risk_warnings}

请执行这个步骤。

执行要求：
1. 充分利用相关知识
2. 使用合适的工具
3. 注意风险点
4. 记录详细过程
5. 评估结果质量

返回JSON格式：
{{{{
  "result": "执行结果（详细）",
  "success": true/false,
  "observations": "观察和发现",
  "tools_used": ["使用的工具"],
  "quality_score": 0-10,
  "confidence": 0.0-1.0,
  "issues_encountered": ["遇到的问题"],
  "needs_replan": true/false,
  "next_step_recommendation": "对下一步的建议"
}}}}
"""


# =================================================================
# 3. Progress & Quality Assessment Prompts
# =================================================================

PROGRESS_ASSESSMENT_PROMPT_TEMPLATE = """任务：{task}

完整计划：
{full_plan}

已完成步骤（{completed_count}/{total_count}）：
{completed_steps}

当前步骤：步骤 {current_step_id}

整体成功标准：
{success_criteria}

请全面评估任务进度。

评估维度：
1. 完成度 - 距离目标还有多远
2. 质量 - 已完成步骤的质量如何
3. 风险 - 是否有新的风险出现
4. 效率 - 是否按预期进度进行
5. 策略 - 当前策略是否有效

返回JSON格式：
{{{{
  "completion_percentage": 0-100,
  "quality_score": 0-10,
  "on_track": true/false,
  "pace": "ahead|on_time|behind",
  "new_risks": ["新风险1"],
  "bottlenecks": ["瓶颈1"],
  "needs_replan": true/false,
  "replan_reason": "重规划原因（如需要）",
  "estimated_remaining_steps": 数字,
  "overall_assessment": "总体评估（详细）",
  "recommendations": ["建议1", "建议2"]
}}}}
"""


QUALITY_ASSESSMENT_PROMPT_TEMPLATE = """任务：{task}

执行计划：
{plan}

所有步骤的执行结果：
{all_results}

最终输出：
{final_output}

成功标准：
{success_criteria}

请评估整体质量。

评估维度：
1. 完整性 - 是否完成所有必要步骤
2. 准确性 - 结果是否准确可靠
3. 效率 - 执行过程是否高效
4. 质量 - 最终输出的质量如何
5. 可用性 - 结果是否可直接使用

返回JSON格式：
{{{{
  "overall_quality_score": 0-10,
  "completeness_score": 0-10,
  "accuracy_score": 0-10,
  "efficiency_score": 0-10,
  "usability_score": 0-10,
  "strengths": ["优点1", "优点2"],
  "weaknesses": ["缺点1", "缺点2"],
  "improvement_suggestions": ["改进建议1"],
  "meets_criteria": true/false,
  "needs_refinement": true/false,
  "assessment_summary": "详细评估总结"
}}}}
"""


# =================================================================
# 4. Final Answer Generation Prompt
# =================================================================

FINAL_ANSWER_PROMPT_TEMPLATE = """任务：{task}

执行计划：
{plan_summary}

所有步骤执行结果：
{execution_results}

质量评估：
{quality_assessment}

请基于完整的执行过程，生成最终答案。

答案要求：
1. 直接回答原始任务
2. 包含详细的解释和依据
3. 提供实施步骤（如需要）
4. 说明局限性和注意事项
5. 给出置信度评估

返回JSON格式：
{{{{
  "final_answer": "清晰、完整的最终答案",
  "explanation": "详细解释（为什么这是答案）",
  "supporting_evidence": ["依据1", "依据2"],
  "implementation_steps": ["实施步骤1", "步骤2"],
  "limitations": "局限性说明",
  "confidence": 0.0-1.0,
  "alternative_solutions": ["备选方案1"],
  "recommendations": ["建议1", "建议2"]
}}}}
"""


# =================================================================
# Helper Functions
# =================================================================

def format_task_analysis_prompt(task: str) -> str:
    """格式化任务分析 prompt"""
    return TASK_ANALYSIS_PROMPT_TEMPLATE.format(task=task)


def format_detailed_plan_prompt(
    task: str,
    task_analysis: str,
    available_tools: str,
    knowledge_base: str
) -> str:
    """格式化详细规划 prompt"""
    return DETAILED_PLAN_PROMPT_TEMPLATE.format(
        task=task,
        task_analysis=task_analysis,
        available_tools=available_tools,
        knowledge_base=knowledge_base
    )


def format_replan_prompt(
    task: str,
    original_plan: str,
    completed_steps: str,
    issue: str,
    failure_analysis: str
) -> str:
    """格式化重规划 prompt"""
    return REPLAN_PROMPT_TEMPLATE.format(
        task=task,
        original_plan=original_plan,
        completed_steps=completed_steps,
        issue=issue,
        failure_analysis=failure_analysis
    )


def format_execute_with_knowledge_prompt(
    step_id: int,
    description: str,
    action_type: str,
    expected_outcome: str,
    task_context: str,
    relevant_knowledge: str,
    previous_results: str,
    available_tools: str,
    risk_warnings: str
) -> str:
    """格式化执行 prompt"""
    return EXECUTE_WITH_KNOWLEDGE_PROMPT_TEMPLATE.format(
        step_id=step_id,
        description=description,
        action_type=action_type,
        expected_outcome=expected_outcome,
        task_context=task_context,
        relevant_knowledge=relevant_knowledge,
        previous_results=previous_results,
        available_tools=available_tools,
        risk_warnings=risk_warnings
    )


def format_progress_assessment_prompt(
    task: str,
    full_plan: str,
    completed_count: int,
    total_count: int,
    completed_steps: str,
    current_step_id: int,
    success_criteria: str
) -> str:
    """格式化进度评估 prompt"""
    return PROGRESS_ASSESSMENT_PROMPT_TEMPLATE.format(
        task=task,
        full_plan=full_plan,
        completed_count=completed_count,
        total_count=total_count,
        completed_steps=completed_steps,
        current_step_id=current_step_id,
        success_criteria=success_criteria
    )


def format_quality_assessment_prompt(
    task: str,
    plan: str,
    all_results: str,
    final_output: str,
    success_criteria: str
) -> str:
    """格式化质量评估 prompt"""
    return QUALITY_ASSESSMENT_PROMPT_TEMPLATE.format(
        task=task,
        plan=plan,
        all_results=all_results,
        final_output=final_output,
        success_criteria=success_criteria
    )


def format_final_answer_prompt(
    task: str,
    plan_summary: str,
    execution_results: str,
    quality_assessment: str
) -> str:
    """格式化最终答案 prompt"""
    return FINAL_ANSWER_PROMPT_TEMPLATE.format(
        task=task,
        plan_summary=plan_summary,
        execution_results=execution_results,
        quality_assessment=quality_assessment
    )
