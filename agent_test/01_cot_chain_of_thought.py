#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Chain-of-Thought (CoT) 思维链推理范式
=====================================

核心思想：通过逐步推理，模拟人类的思维过程，将复杂问题分解为多个推理步骤。

特点：
- 线性推理流程：分析 → 推理 → 结论
- 每一步都有明确的推理依据
- 适用于需要多步骤推理的问题
"""

from typing import TypedDict, List, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from utils import get_llm
from log_utils import log_node_input, log_node_output, log_prompt
from prompts.cot_prompts import (
    COT_SYSTEM_PROMPT,
    format_analyze_prompt,
    format_reasoning_prompt,
    format_conclude_prompt
)
import json


# =================================================================
# 状态定义
# =================================================================

class CoTState(TypedDict):
    """CoT 推理状态"""
    question: str  # 原始问题
    reasoning_steps: List[Dict[str, str]]  # 推理步骤列表
    final_answer: str  # 最终答案
    current_step: int  # 当前步骤编号


# =================================================================
# 节点函数
# =================================================================

def analyze_question_node(state: CoTState) -> Dict[str, Any]:
    """分析问题节点 - 提取关键信息"""
    
    log_node_input("analyze_question_node", state)
    
    question = state["question"]
    llm = get_llm(temperature=0.3)
    
    # 使用 prompt 模板
    human_prompt = format_analyze_prompt(question)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", COT_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    # 记录完整的 prompt
    log_prompt("analyze_question_node", [
        ("system", COT_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析结果
    try:
        import re
        json_str = re.search(r'\{.*\}', result.content, re.DOTALL)
        if json_str:
            analysis = json.loads(json_str.group())
        else:
            analysis = {"key_elements": [], "constraints": [], "analysis": result.content}
    except:
        analysis = {"key_elements": [], "constraints": [], "analysis": result.content}
    
    reasoning_step = {
        "step_number": 1,
        "step_name": "问题分析",
        "content": analysis.get("analysis", ""),
        "key_elements": analysis.get("key_elements", []),
        "reasoning": "提取问题的关键要素和约束条件"
    }
    
    output = {
        "reasoning_steps": [reasoning_step],
        "current_step": 1
    }
    
    log_node_output("analyze_question_node", output)
    
    return output


def reasoning_node(state: CoTState) -> Dict[str, Any]:
    """推理节点 - 逐步推理"""
    
    log_node_input("reasoning_node", state)
    
    question = state["question"]
    reasoning_steps = state.get("reasoning_steps", [])
    current_step = state.get("current_step", 1)
    
    # 构建已有推理步骤的上下文
    context = ""
    for step in reasoning_steps:
        context += f"\n步骤{step['step_number']}: {step['step_name']}\n"
        context += f"内容: {step['content']}\n"
    
    # 计算剩余推理步骤
    max_steps = 3  # 最多3步推理
    remaining_steps = max_steps - current_step
    is_last_step = remaining_steps <= 1
    
    llm = get_llm(temperature=0.3)
    
    # 使用 prompt 模板
    human_prompt = format_reasoning_prompt(
        question=question,
        context=context,
        current_step=current_step,
        max_steps=max_steps,
        remaining_steps=remaining_steps,
        is_last_step=is_last_step
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", COT_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    # 记录完整的 prompt
    log_prompt("reasoning_node", [
        ("system", COT_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析结果
    try:
        import re
        json_str = re.search(r'\{.*\}', result.content, re.DOTALL)
        if json_str:
            step_data = json.loads(json_str.group())
        else:
            step_data = {
                "step_name": f"步骤{current_step + 1}",
                "content": result.content,
                "reasoning": "",
                "next_action": "",
                "can_conclude": False
            }
    except:
        step_data = {
            "step_name": f"步骤{current_step + 1}",
            "content": result.content,
            "reasoning": "",
            "next_action": "",
            "can_conclude": False
        }
    
    new_step = {
        "step_number": current_step + 1,
        "step_name": step_data.get("step_name", f"步骤{current_step + 1}"),
        "content": step_data.get("content", ""),
        "reasoning": step_data.get("reasoning", ""),
        "next_action": step_data.get("next_action", ""),
        "can_conclude": step_data.get("can_conclude", False)
    }
    
    reasoning_steps.append(new_step)
    
    output = {
        "reasoning_steps": reasoning_steps,
        "current_step": current_step + 1
    }
    
    log_node_output("reasoning_node", output)
    
    return output


def conclude_node(state: CoTState) -> Dict[str, Any]:
    """结论节点 - 得出最终答案"""
    
    log_node_input("conclude_node", state)
    
    question = state["question"]
    reasoning_steps = state.get("reasoning_steps", [])
    
    # 构建完整推理过程
    context = ""
    for step in reasoning_steps:
        context += f"\n步骤{step['step_number']}: {step['step_name']}\n"
        context += f"内容: {step['content']}\n"
        if step.get('reasoning'):
            context += f"推理依据: {step['reasoning']}\n"
    
    llm = get_llm(temperature=0.3)
    
    # 使用 prompt 模板
    human_prompt = format_conclude_prompt(question=question, context=context)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", COT_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    # 记录完整的 prompt
    log_prompt("conclude_node", [
        ("system", COT_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析结果
    try:
        import re
        json_str = re.search(r'\{.*\}', result.content, re.DOTALL)
        if json_str:
            conclusion = json.loads(json_str.group())
        else:
            conclusion = {"final_answer": result.content, "summary": "", "confidence": "中"}
    except:
        conclusion = {"final_answer": result.content, "summary": "", "confidence": "中"}
    
    output = {
        "final_answer": conclusion.get("final_answer", result.content),
        "reasoning_steps": reasoning_steps + [{
            "step_number": len(reasoning_steps) + 1,
            "step_name": "最终结论",
            "content": conclusion.get("final_answer", ""),
            "summary": conclusion.get("summary", ""),
            "confidence": conclusion.get("confidence", "中")
        }]
    }
    
    log_node_output("conclude_node", output)
    
    return output


def should_continue_reasoning(state: CoTState) -> str:
    """判断是否继续推理"""
    current_step = state.get("current_step", 1)
    reasoning_steps = state.get("reasoning_steps", [])
    
    # 检查是否已经达到最大步数（最多3步推理）
    if current_step >= 3:
        return "conclude"
    
    # 检查最近的推理步骤是否表示可以提前结束
    if reasoning_steps:
        last_step = reasoning_steps[-1]
        # 如果 LLM 明确表示可以结束推理
        if last_step.get("can_conclude", False):
            return "conclude"
        # 如果 next_action 明确表示可以得出最终答案
        next_action = last_step.get("next_action", "").lower()
        if "得出最终答案" in next_action or "conclude" in next_action or "结束" in next_action:
            return "conclude"
    
    return "reason"


# =================================================================
# 构建图
# =================================================================

def create_cot_graph():
    """创建 CoT 推理图"""
    
    graph = StateGraph(CoTState)
    
    # 添加节点
    graph.add_node("analyze", analyze_question_node)
    graph.add_node("reason", reasoning_node)
    graph.add_node("conclude", conclude_node)
    
    # 添加边
    graph.set_entry_point("analyze")
    graph.add_edge("analyze", "reason")
    graph.add_conditional_edges(
        "reason",
        should_continue_reasoning,
        {
            "reason": "reason",  # 继续推理
            "conclude": "conclude"  # 得出结论
        }
    )
    graph.add_edge("conclude", END)
    
    return graph.compile()


# =================================================================
# Demo 示例
# =================================================================

def demo_cot():
    """CoT 推理 Demo"""
    
    print("=" * 60)
    print("Chain-of-Thought (CoT) 思维链推理 Demo")
    print("=" * 60)
    
    # 创建图
    graph = create_cot_graph()
    
    # 测试问题
    test_questions = [
        # "如果一个数的3倍加上5等于20，这个数是多少？",
        # "为什么天空是蓝色的？",
        "如何提高工作效率？"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n【问题 {i}】")
        print(f"问题：{question}\n")
        
        # 运行推理
        initial_state = {
            "question": question,
            "reasoning_steps": [],
            "final_answer": "",
            "current_step": 0
        }
        
        result = graph.invoke(initial_state)
        
        # 显示结果
        print("推理过程：")
        for step in result["reasoning_steps"]:
            print(f"\n步骤 {step['step_number']}: {step['step_name']}")
            print(f"  内容: {step['content']}")
            if step.get('reasoning'):
                print(f"  推理依据: {step['reasoning']}")
        
        print(f"\n最终答案：{result['final_answer']}")
        print("-" * 60)


if __name__ == "__main__":
    demo_cot()
