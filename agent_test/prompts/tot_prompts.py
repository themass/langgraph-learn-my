#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tree of Thoughts (ToT) Prompt 模板配置
所有 prompt 模板都在这里定义，避免代码拼接，提高可读性
"""

import re


# =================================================================
# System Prompt
# =================================================================

TOT_SYSTEM_PROMPT = """你是一个使用思维树(Tree of Thoughts)方法解决问题的专家。

工作流程：
1. 生成多个候选推理路径
2. 评估每个路径的质量和可行性
3. 选择最有希望的路径继续扩展
4. 重复直到找到解决方案

生成候选路径时，要考虑：
- 不同的推理角度
- 不同的解决策略
- 不同的假设条件

评估路径时，要考虑：
- 逻辑严密性
- 可行性
- 解决问题的潜力
"""


# =================================================================
# Generate Paths Node Prompt Template
# =================================================================

TOT_GENERATE_PROMPT_TEMPLATE = """问题：{question}

当前状态：{current_state}

已有路径：{existing_paths}

请生成3-5个不同的推理路径或解决思路。每个路径应该：
1. 有明确的推理方向
2. 有具体的步骤
3. 有合理的假设

返回JSON格式：
{{{{"paths": [{{{{"path_id": 1, "direction": "路径方向描述", "steps": ["步骤1", "步骤2"], "assumptions": ["假设1", "假设2"]}}}}]}}}}
"""


# =================================================================
# Evaluate Paths Node Prompt Template
# =================================================================

TOT_EVALUATE_PROMPT_TEMPLATE = """问题：{question}

候选路径：
{paths}

请评估每个路径的质量，返回JSON格式：
{{{{"evaluations": [{{{{"path_id": 1, "score": 8, "reasoning": "评分理由", "feasibility": "可行性评估", "potential": "解决问题的潜力"}}}}], "best_path_id": 1}}}}
"""


# =================================================================
# Expand Path Node Prompt Template
# =================================================================

TOT_EXPAND_PROMPT_TEMPLATE = """问题：{question}

当前最佳路径：
方向：{direction}
步骤：{steps}

请基于这个路径继续深入推理，给出更详细的答案。返回JSON格式：
{{"answer": "最终答案", "reasoning": "推理过程", "confidence": "信心程度（高/中/低）"}}
"""


# =================================================================
# Helper Functions
# =================================================================

def format_generate_prompt(
    question: str,
    current_state: str,
    existing_paths: str
) -> str:
    """格式化生成路径节点 prompt"""
    prompt = TOT_GENERATE_PROMPT_TEMPLATE.format(
        question=question,
        current_state=current_state,
        existing_paths=existing_paths
    )
    # 转义 JSON 示例中的花括号
    # 模板中使用4个花括号 {{{{ 表示需要转义为 {{ 的花括号
    # format 后变成 {{，然后我们需要确保它们被正确转义
    # 由于模板中已经使用了4个花括号，format后会变成2个花括号，这正是我们需要的
    return prompt


def format_evaluate_prompt(question: str, paths: str) -> str:
    """格式化评估路径节点 prompt"""
    prompt = TOT_EVALUATE_PROMPT_TEMPLATE.format(
        question=question,
        paths=paths
    )
    # 转义 JSON 示例中的花括号
    # 模板中使用4个花括号 {{{{ 表示需要转义为 {{ 的花括号
    # format 后变成 {{，然后我们需要确保它们被正确转义
    # 由于模板中已经使用了4个花括号，format后会变成2个花括号，这正是我们需要的
    return prompt


def format_expand_prompt(question: str, direction: str, steps: str) -> str:
    """格式化扩展路径节点 prompt"""
    prompt = TOT_EXPAND_PROMPT_TEMPLATE.format(
        question=question,
        direction=direction,
        steps=steps
    )
    # 转义 JSON 示例中的花括号
    # 模板中使用4个花括号 {{{{ 表示需要转义为 {{ 的花括号
    # format 后变成 {{，然后我们需要确保它们被正确转义
    # 由于模板中已经使用了4个花括号，format后会变成2个花括号，这正是我们需要的
    return prompt
