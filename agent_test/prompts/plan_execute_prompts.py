#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Plan-and-Execute Prompt 模板配置
所有 prompt 模板都在这里定义，避免代码拼接，提高可读性
"""

import re


# =================================================================
# System Prompt
# =================================================================

PLAN_EXECUTE_SYSTEM_PROMPT = """你是一个使用 Plan-and-Execute 策略解决问题的专家。

工作流程：
1. Plan（规划）：将复杂任务分解为可执行的步骤序列
2. Execute（执行）：依次执行每个步骤
3. Progress Check（检查）：评估完成情况
4. Re-plan（重新规划）：如果需要，调整计划

规划原则：
- 将复杂任务分解为简单、可执行的步骤
- 每个步骤应该是原子性的、可验证的
- 步骤之间应该有明确的依赖关系
- 保持计划的灵活性，允许调整

执行原则：
- 严格按照计划执行
- 记录每步的执行结果
- 遇到问题及时反馈
- 必要时请求重新规划
"""


# =================================================================
# Plan Node Prompt Templates
# =================================================================

PLAN_PROMPT_TEMPLATE = """任务：{task}

{context}

请将这个任务分解为可执行的步骤序列。

要求：
1. 每个步骤应该清晰、具体、可执行
2. 步骤之间应该有逻辑顺序
3. 考虑可能需要的工具或资源
4. 估计每个步骤的复杂度

返回JSON格式：
{{{{
  "plan": [
    {{{{
      "step_id": 1,
      "description": "步骤描述",
      "action_type": "search|calculate|analyze|synthesize",
      "dependencies": [],
      "estimated_complexity": "low|medium|high"
    }}}}
  ],
  "overall_strategy": "整体策略说明",
  "success_criteria": "成功标准"
}}}}
"""


REPLAN_PROMPT_TEMPLATE = """原始任务：{task}

原计划：
{original_plan}

已完成步骤：
{completed_steps}

当前问题：{issue}

请重新规划剩余步骤。考虑：
1. 已完成的步骤和结果
2. 遇到的问题和障碍
3. 需要调整的地方
4. 新的执行策略

返回JSON格式：
{{{{
  "revised_plan": [
    {{{{
      "step_id": n,
      "description": "步骤描述",
      "action_type": "类型",
      "dependencies": [],
      "estimated_complexity": "复杂度"
    }}}}
  ],
  "changes_explanation": "调整原因说明",
  "new_strategy": "新策略"
}}}}
"""


# =================================================================
# Execute Node Prompt Template
# =================================================================

EXECUTE_PROMPT_TEMPLATE = """当前步骤：
步骤ID：{step_id}
描述：{description}
行动类型：{action_type}

{context}

已完成的步骤结果：
{previous_results}

可用工具：
{available_tools}

请执行这个步骤，并返回结果。

返回JSON格式：
{{{{
  "result": "执行结果",
  "success": true/false,
  "observations": "观察和发现",
  "next_step_suggestion": "对下一步的建议（可选）",
  "needs_replan": true/false,
  "issue": "遇到的问题（如果有）"
}}}}
"""


# =================================================================
# Progress Check Node Prompt Template
# =================================================================

PROGRESS_CHECK_PROMPT_TEMPLATE = """任务：{task}

完整计划：
{plan}

已完成步骤：
{completed_steps}

当前步骤：{current_step_id}

请评估任务完成进度。

评估要点：
1. 当前完成百分比
2. 是否按计划进行
3. 是否遇到阻碍
4. 是否需要调整计划
5. 预计何时完成

返回JSON格式：
{{{{
  "completion_percentage": 0-100,
  "on_track": true/false,
  "issues": ["问题1", "问题2"],
  "needs_replan": true/false,
  "estimated_remaining_steps": 数字,
  "overall_assessment": "总体评估"
}}}}
"""


# =================================================================
# Finish Node Prompt Template  
# =================================================================

FINISH_PROMPT_TEMPLATE = """任务：{task}

执行计划：
{plan}

所有步骤的执行结果：
{all_results}

请基于完整的执行过程，生成最终答案和总结。

返回JSON格式：
{{{{
  "final_answer": "最终答案",
  "summary": "执行总结",
  "key_findings": ["发现1", "发现2"],
  "challenges_overcome": ["克服的挑战1", "挑战2"],
  "quality_assessment": "质量评估（高/中/低）"
}}}}
"""


# =================================================================
# Helper Functions
# =================================================================

def format_plan_prompt(task: str, context: str = "") -> str:
    """格式化规划节点 prompt"""
    context_text = f"\n背景信息：\n{context}\n" if context else ""
    return PLAN_PROMPT_TEMPLATE.format(task=task, context=context_text)


def format_replan_prompt(
    task: str,
    original_plan: str,
    completed_steps: str,
    issue: str
) -> str:
    """格式化重新规划 prompt"""
    return REPLAN_PROMPT_TEMPLATE.format(
        task=task,
        original_plan=original_plan,
        completed_steps=completed_steps,
        issue=issue
    )


def format_execute_prompt(
    step_id: int,
    description: str,
    action_type: str,
    context: str,
    previous_results: str,
    available_tools: str
) -> str:
    """格式化执行节点 prompt"""
    context_text = f"\n相关背景：\n{context}\n" if context else ""
    return EXECUTE_PROMPT_TEMPLATE.format(
        step_id=step_id,
        description=description,
        action_type=action_type,
        context=context_text,
        previous_results=previous_results if previous_results else "无",
        available_tools=available_tools
    )


def format_progress_check_prompt(
    task: str,
    plan: str,
    completed_steps: str,
    current_step_id: int
) -> str:
    """格式化进度检查 prompt"""
    return PROGRESS_CHECK_PROMPT_TEMPLATE.format(
        task=task,
        plan=plan,
        completed_steps=completed_steps,
        current_step_id=current_step_id
    )


def format_finish_prompt(
    task: str,
    plan: str,
    all_results: str
) -> str:
    """格式化完成节点 prompt"""
    return FINISH_PROMPT_TEMPLATE.format(
        task=task,
        plan=plan,
        all_results=all_results
    )
