 #!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ReAct (Reasoning + Acting) Prompt 模板配置
所有 prompt 模板都在这里定义，避免代码拼接，提高可读性
"""

import re


# =================================================================
# System Prompt
# =================================================================

REACT_SYSTEM_PROMPT = """你是一个智能代理，使用 ReAct (Reasoning + Acting) 模式解决问题。

工作流程：
1. 思考(Think)：分析当前情况，决定下一步行动
2. 行动(Act)：执行选定的行动
3. 观察(Observe)：观察行动结果，更新理解
4. 重复直到任务完成

思考格式：
Thought: [你的思考过程]
- 当前情况：[描述当前状态]
- 目标：[要达成的目标]
- 可用行动：[可执行的行动列表]
- 选择行动：[选择的行动及原因]

行动格式：
Action: [行动名称]
Action Input: [行动参数]

观察格式：
Observation: [行动的结果]
"""


# =================================================================
# Think Node Prompt Template
# =================================================================

REACT_THINK_PROMPT_TEMPLATE = """任务：{task}

当前观察：{observation}

历史记录：{history_text}

可用工具：
{tools_desc}

请思考下一步应该做什么。返回JSON格式：
{{"thought": "你的思考过程", "action": "行动名称（finish表示任务完成）", "action_input": "行动所需的输入参数", "reasoning": "为什么选择这个行动"}}
"""


# =================================================================
# Finish Node Prompt Template
# =================================================================

REACT_FINISH_PROMPT_TEMPLATE = """任务：{task}

执行历史：
{history_text}

请基于以上执行历史，给出最终答案。返回JSON格式：
{{"final_answer": "明确的最终答案", "summary": "任务执行总结"}}
"""


# =================================================================
# Helper Functions
# =================================================================

def format_think_prompt(
    task: str,
    observation: str,
    history_text: str,
    tools_desc: str
) -> str:
    """格式化思考节点 prompt"""
    prompt = REACT_THINK_PROMPT_TEMPLATE.format(
        task=task,
        observation=observation if observation else "无",
        history_text=history_text if history_text else "无",
        tools_desc=tools_desc
    )
    # 转义 JSON 示例中的花括号
    json_pattern = r'(\{[^}]*\})'
    def escape_braces(match):
        json_str = match.group(1)
        escaped = json_str.replace('{', '{{').replace('}', '}}')
        return escaped
    prompt = re.sub(json_pattern, escape_braces, prompt)
    return prompt


def format_finish_prompt(task: str, history_text: str) -> str:
    """格式化完成节点 prompt"""
    prompt = REACT_FINISH_PROMPT_TEMPLATE.format(
        task=task,
        history_text=history_text
    )
    # 转义 JSON 示例中的花括号
    json_pattern = r'(\{[^}]*\})'
    def escape_braces(match):
        json_str = match.group(1)
        escaped = json_str.replace('{', '{{').replace('}', '}}')
        return escaped
    prompt = re.sub(json_pattern, escape_braces, prompt)
    return prompt
