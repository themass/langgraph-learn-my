#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Self-Reflection 自我反思范式
============================

核心思想：生成初步答案后，对其进行自我评估和修正，形成反馈循环，持续改进答案质量。

特点：
- 生成初始答案
- 自我评估答案质量
- 识别问题和不足
- 改进答案
- 循环直到达到质量标准
"""

from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from utils import get_llm
from log_utils import log_node_input, log_node_output, log_prompt
from prompts.self_reflection_prompts import (
    SELF_REFLECTION_SYSTEM_PROMPT,
    format_generate_prompt as format_sr_generate_prompt,
    format_reflect_prompt,
    format_improve_prompt
)
import json


# =================================================================
# 状态定义
# =================================================================

class SelfReflectionState(TypedDict):
    """Self-Reflection 状态"""
    question: str  # 原始问题
    current_answer: Optional[str]  # 当前答案
    reasoning: Optional[str]  # 当前推理过程
    reflection: Optional[Dict[str, Any]]  # 反思结果
    iteration: int  # 迭代次数
    quality_score: Optional[float]  # 质量分数
    final_answer: Optional[str]  # 最终答案
    finished: bool  # 是否完成


# =================================================================
# 节点函数
# =================================================================

def generate_answer_node(state: SelfReflectionState) -> Dict[str, Any]:
    """生成初始答案节点"""
    
    log_node_input("generate_answer_node", state)
    
    question = state["question"]
    
    llm = get_llm(temperature=0.5)
    
    # 使用 prompt 模板
    human_prompt = format_sr_generate_prompt(question=question)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SELF_REFLECTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    # 记录完整的 prompt
    log_prompt("generate_answer_node", [
        ("system", SELF_REFLECTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析结果
    try:
        import re
        json_str = re.search(r'\{.*\}', result.content, re.DOTALL)
        if json_str:
            answer_data = json.loads(json_str.group())
        else:
            answer_data = {
                "answer": result.content,
                "reasoning": "",
                "key_points": []
            }
    except:
        answer_data = {
            "answer": result.content,
            "reasoning": "",
            "key_points": []
        }
    
    output = {
        "current_answer": answer_data.get("answer", ""),
        "reasoning": answer_data.get("reasoning", ""),
        "iteration": 1
    }
    
    log_node_output("generate_answer_node", output)
    
    return output


def reflect_node(state: SelfReflectionState) -> Dict[str, Any]:
    """反思节点 - 评估答案质量"""
    
    log_node_input("reflect_node", state)
    
    question = state["question"]
    current_answer = state.get("current_answer", "")
    reasoning = state.get("reasoning", "")
    
    llm = get_llm(temperature=0.3)
    
    # 使用 prompt 模板
    human_prompt = format_reflect_prompt(
        question=question,
        current_answer=current_answer,
        reasoning=reasoning
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SELF_REFLECTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    # 记录完整的 prompt
    log_prompt("reflect_node", [
        ("system", SELF_REFLECTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析结果
    try:
        import re
        json_str = re.search(r'\{.*\}', result.content, re.DOTALL)
        if json_str:
            reflection_data = json.loads(json_str.group())
        else:
            reflection_data = {
                "quality_score": 5,
                "strengths": [],
                "weaknesses": ["需要更多信息"],
                "improvements": ["改进答案"],
                "is_sufficient": False
            }
    except:
        reflection_data = {
            "quality_score": 5,
            "strengths": [],
            "weaknesses": ["需要更多信息"],
            "improvements": ["改进答案"],
                "is_sufficient": False
        }
    
    output = {
        "reflection": reflection_data,
        "quality_score": reflection_data.get("quality_score", 5)
    }
    
    log_node_output("reflect_node", output)
    
    log_node_output("reflect_node", output)
    
    return output


def improve_answer_node(state: SelfReflectionState) -> Dict[str, Any]:
    """改进答案节点"""
    
    log_node_input("improve_answer_node", state)
    
    question = state["question"]
    current_answer = state.get("current_answer", "")
    reflection = state.get("reflection", {})
    iteration = state.get("iteration", 1)
    
    strengths = reflection.get("strengths", [])
    weaknesses = reflection.get("weaknesses", [])
    improvements = reflection.get("improvements", [])
    
    llm = get_llm(temperature=0.3)
    
    # 使用 prompt 模板
    human_prompt = format_improve_prompt(
        question=question,
        current_answer=current_answer,
        strengths=", ".join(strengths) if strengths else "无",
        weaknesses=", ".join(weaknesses) if weaknesses else "无",
        improvements=", ".join(improvements) if improvements else "无"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SELF_REFLECTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    # 记录完整的 prompt
    log_prompt("improve_answer_node", [
        ("system", SELF_REFLECTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析结果
    try:
        import re
        json_str = re.search(r'\{.*\}', result.content, re.DOTALL)
        if json_str:
            improved_data = json.loads(json_str.group())
        else:
            improved_data = {
                "improved_answer": result.content,
                "improvements_made": [],
                "reasoning": ""
            }
    except:
        improved_data = {
            "improved_answer": result.content,
            "improvements_made": [],
            "reasoning": ""
        }
    
    output = {
        "current_answer": improved_data.get("improved_answer", ""),
        "reasoning": improved_data.get("reasoning", ""),
        "iteration": iteration + 1
    }
    
    log_node_output("improve_answer_node", output)
    
    log_node_output("improve_answer_node", output)
    
    return output


def should_continue_reflecting(state: SelfReflectionState) -> str:
    """判断是否继续反思"""
    reflection = state.get("reflection", {})
    iteration = state.get("iteration", 1)
    quality_score = state.get("quality_score", 0)
    
    # 如果达到质量标准或迭代次数过多，则完成
    if reflection.get("is_sufficient", False) or quality_score >= 8:
        return "finish"
    
    if iteration >= 3:  # 最多3次迭代
        return "finish"
    
    return "improve"


def finish_node(state: SelfReflectionState) -> Dict[str, Any]:
    """完成节点"""
    
    log_node_input("finish_node", state)
    
    output = {
        "final_answer": state.get("current_answer", ""),
        "finished": True
    }
    
    log_node_output("finish_node", output)
    
    return output


# =================================================================
# 构建图
# =================================================================

def create_self_reflection_graph():
    """创建 Self-Reflection 图"""
    
    graph = StateGraph(SelfReflectionState)
    
    # 添加节点
    graph.add_node("generate", generate_answer_node)
    graph.add_node("reflect", reflect_node)
    graph.add_node("improve", improve_answer_node)
    graph.add_node("finish", finish_node)
    
    # 添加边
    graph.set_entry_point("generate")
    graph.add_edge("generate", "reflect")
    graph.add_conditional_edges(
        "reflect",
        should_continue_reflecting,
        {
            "improve": "improve",  # 继续改进
            "finish": "finish"  # 完成
        }
    )
    graph.add_edge("improve", "reflect")  # 改进后重新反思
    graph.add_edge("finish", END)
    
    return graph.compile()


# =================================================================
# Demo 示例
# =================================================================

def demo_self_reflection():
    """Self-Reflection Demo"""
    
    print("=" * 60)
    print("Self-Reflection 自我反思 Demo")
    print("=" * 60)
    
    # 创建图
    graph = create_self_reflection_graph()
    
    # 测试问题
    test_questions = [
        "解释什么是机器学习？",
        "如何提高工作效率？请给出具体建议。"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n【问题 {i}】")
        print(f"问题：{question}\n")
        
        # 运行反思循环
        initial_state = {
            "question": question,
            "current_answer": None,
            "reasoning": None,
            "reflection": None,
            "iteration": 0,
            "quality_score": None,
            "final_answer": None,
            "finished": False
        }
        
        result = graph.invoke(initial_state)
        
        # 显示结果
        print(f"迭代次数: {result.get('iteration', 0)}")
        print(f"质量分数: {result.get('quality_score', 0)}/10")
        
        reflection = result.get("reflection", {})
        if reflection:
            print(f"\n反思结果:")
            print(f"  优点: {', '.join(reflection.get('strengths', []))}")
            print(f"  缺点: {', '.join(reflection.get('weaknesses', []))}")
            print(f"  改进建议: {', '.join(reflection.get('improvements', []))}")
        
        print(f"\n最终答案：{result.get('final_answer', '未完成')}")
        print("-" * 60)


if __name__ == "__main__":
    demo_self_reflection()
