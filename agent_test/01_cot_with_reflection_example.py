#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CoT 模式 + 反思模块示例
========================

展示如何为 CoT 模式添加轻量级反思功能

特点：
- 在推理过程中加入质量检查
- 发现推理错误和遗漏
- 改进推理质量
- 可选启用（根据配置决定是否使用反思）
"""

from typing import TypedDict, List, Dict, Any, Optional
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
from prompts.reflection_prompts import (
    COT_REFLECTION_SYSTEM_PROMPT,
    format_cot_reflection_prompt
)
import json
import re


# =================================================================
# 状态定义（扩展 CoT 状态，添加反思相关字段）
# =================================================================

class CoTWithReflectionState(TypedDict):
    """CoT 推理状态（带反思）"""
    question: str  # 原始问题
    reasoning_steps: List[Dict[str, str]]  # 推理步骤列表
    final_answer: str  # 最终答案
    current_step: int  # 当前步骤编号
    enable_reflection: bool  # 是否启用反思
    reflection_results: Optional[List[Dict[str, Any]]]  # 反思结果列表
    quality_scores: Optional[List[float]]  # 质量分数列表


# =================================================================
# 反思节点（新增）
# =================================================================

def quality_check_node(state: CoTWithReflectionState) -> Dict[str, Any]:
    """质量检查节点 - 评估当前推理质量"""
    
    log_node_input("quality_check_node", state)
    
    # 如果未启用反思，直接跳过
    if not state.get("enable_reflection", False):
        output = {
            "quality_scores": state.get("quality_scores", []),
            "reflection_results": state.get("reflection_results", [])
        }
        log_node_output("quality_check_node", output)
        return output
    
    question = state["question"]
    reasoning_steps = state.get("reasoning_steps", [])
    current_step = state.get("current_step", 1)
    max_steps = 3
    
    # 构建推理步骤文本
    reasoning_text = ""
    for step in reasoning_steps:
        reasoning_text += f"\n步骤{step['step_number']}: {step['step_name']}\n"
        reasoning_text += f"内容: {step['content']}\n"
        if step.get('reasoning'):
            reasoning_text += f"推理依据: {step['reasoning']}\n"
    
    llm = get_llm(temperature=0.2)  # 低温度以获得客观评估
    
    # 格式化反思 Prompt
    human_prompt = format_cot_reflection_prompt(
        question=question,
        reasoning_steps=reasoning_text,
        current_step=current_step,
        max_steps=max_steps
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", COT_REFLECTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    log_prompt("quality_check_node", [
        ("system", COT_REFLECTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析结果
    try:
        json_str = re.search(r'\{.*\}', result.content, re.DOTALL)
        if json_str:
            reflection_data = json.loads(json_str.group())
        else:
            reflection_data = {
                "quality_score": 7.0,
                "issues": [],
                "strengths": [],
                "needs_improvement": False,
                "improvement_suggestions": []
            }
    except:
        reflection_data = {
            "quality_score": 7.0,
            "issues": [],
            "strengths": [],
            "needs_improvement": False,
            "improvement_suggestions": []
        }
    
    quality_score = reflection_data.get("quality_score", 7.0)
    needs_improvement = reflection_data.get("needs_improvement", False)
    
    # 更新质量分数和反思结果
    quality_scores = state.get("quality_scores", [])
    quality_scores.append(quality_score)
    
    reflection_results = state.get("reflection_results", [])
    reflection_results.append({
        "step": current_step,
        "quality_score": quality_score,
        "issues": reflection_data.get("issues", []),
        "strengths": reflection_data.get("strengths", []),
        "improvement_suggestions": reflection_data.get("improvement_suggestions", []),
        "needs_improvement": needs_improvement
    })
    
    output = {
        "quality_scores": quality_scores,
        "reflection_results": reflection_results,
        "needs_improvement": needs_improvement,
        "current_quality_score": quality_score
    }
    
    log_node_output("quality_check_node", output)
    
    return output


def should_improve_reasoning(state: CoTWithReflectionState) -> str:
    """判断是否需要改进推理"""
    
    # 如果未启用反思，直接继续
    if not state.get("enable_reflection", False):
        return "continue"
    
    # 检查是否需要改进
    needs_improvement = state.get("needs_improvement", False)
    current_quality_score = state.get("current_quality_score", 7.0)
    current_step = state.get("current_step", 1)
    
    # 如果质量分数低于阈值（6.0）且不是最后一步，建议改进
    if needs_improvement and current_quality_score < 6.0 and current_step < 3:
        return "improve"
    
    return "continue"


# =================================================================
# 复用原有的 CoT 节点（简化版，实际应该从原文件导入）
# =================================================================

def analyze_question_node(state: CoTWithReflectionState) -> Dict[str, Any]:
    """分析问题节点 - 提取关键信息"""
    # 这里简化实现，实际应该复用原文件中的函数
    log_node_input("analyze_question_node", state)
    
    question = state["question"]
    llm = get_llm(temperature=0.3)
    
    human_prompt = format_analyze_prompt(question)
    prompt = ChatPromptTemplate.from_messages([
        ("system", COT_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    log_prompt("analyze_question_node", [
        ("system", COT_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    try:
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


def reasoning_node(state: CoTWithReflectionState) -> Dict[str, Any]:
    """推理节点 - 逐步推理"""
    log_node_input("reasoning_node", state)
    
    question = state["question"]
    reasoning_steps = state.get("reasoning_steps", [])
    current_step = state.get("current_step", 1)
    
    context = ""
    for step in reasoning_steps:
        context += f"\n步骤{step['step_number']}: {step['step_name']}\n"
        context += f"内容: {step['content']}\n"
    
    max_steps = 3
    remaining_steps = max_steps - current_step
    is_last_step = remaining_steps <= 1
    
    llm = get_llm(temperature=0.3)
    
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
    
    log_prompt("reasoning_node", [
        ("system", COT_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    try:
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


def conclude_node(state: CoTWithReflectionState) -> Dict[str, Any]:
    """结论节点 - 得出最终答案"""
    log_node_input("conclude_node", state)
    
    question = state["question"]
    reasoning_steps = state.get("reasoning_steps", [])
    
    context = ""
    for step in reasoning_steps:
        context += f"\n步骤{step['step_number']}: {step['step_name']}\n"
        context += f"内容: {step['content']}\n"
        if step.get('reasoning'):
            context += f"推理依据: {step['reasoning']}\n"
    
    llm = get_llm(temperature=0.3)
    
    human_prompt = format_conclude_prompt(question=question, context=context)
    prompt = ChatPromptTemplate.from_messages([
        ("system", COT_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    log_prompt("conclude_node", [
        ("system", COT_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    try:
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


def should_continue_reasoning(state: CoTWithReflectionState) -> str:
    """判断是否继续推理"""
    current_step = state.get("current_step", 1)
    reasoning_steps = state.get("reasoning_steps", [])
    
    if current_step >= 3:
        return "conclude"
    
    if reasoning_steps:
        last_step = reasoning_steps[-1]
        if last_step.get("can_conclude", False):
            return "conclude"
        next_action = last_step.get("next_action", "").lower()
        if "得出最终答案" in next_action or "conclude" in next_action or "结束" in next_action:
            return "conclude"
    
    # 如果启用反思，先进行质量检查
    if state.get("enable_reflection", False):
        return "quality_check"
    
    return "reason"


# =================================================================
# 构建图（带反思功能）
# =================================================================

def create_cot_with_reflection_graph(enable_reflection: bool = True):
    """创建 CoT 推理图（带反思功能）"""
    
    graph = StateGraph(CoTWithReflectionState)
    
    # 添加节点
    graph.add_node("analyze", analyze_question_node)
    graph.add_node("reason", reasoning_node)
    graph.add_node("quality_check", quality_check_node)  # 新增反思节点
    graph.add_node("conclude", conclude_node)
    
    # 添加边
    graph.set_entry_point("analyze")
    graph.add_edge("analyze", "reason")
    
    # 推理节点的条件边
    graph.add_conditional_edges(
        "reason",
        should_continue_reasoning,
        {
            "reason": "reason",  # 继续推理
            "quality_check": "quality_check",  # 质量检查（如果启用反思）
            "conclude": "conclude"  # 得出结论
        }
    )
    
    # 质量检查节点的条件边
    graph.add_conditional_edges(
        "quality_check",
        should_improve_reasoning,
        {
            "improve": "reason",  # 改进推理
            "continue": "conclude"  # 继续到结论
        }
    )
    
    graph.add_edge("conclude", END)
    
    return graph.compile()


# =================================================================
# Demo 示例
# =================================================================

def demo_cot_with_reflection():
    """CoT + 反思 Demo"""
    
    print("=" * 60)
    print("Chain-of-Thought (CoT) + 反思模块 Demo")
    print("=" * 60)
    
    # 测试问题
    test_questions = [
        "为什么天空是蓝色的？请详细解释。"
    ]
    
    # 测试启用和禁用反思两种情况
    for enable_reflection in [True, False]:
        print(f"\n{'='*60}")
        print(f"【{'启用' if enable_reflection else '禁用'}反思模式】")
        print(f"{'='*60}")
        
        graph = create_cot_with_reflection_graph(enable_reflection=enable_reflection)
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n【问题 {i}】")
            print(f"问题：{question}\n")
            
            initial_state = {
                "question": question,
                "reasoning_steps": [],
                "final_answer": "",
                "current_step": 0,
                "enable_reflection": enable_reflection,
                "reflection_results": [],
                "quality_scores": []
            }
            
            result = graph.invoke(initial_state)
            
            # 显示结果
            print("\n推理过程：")
            for step in result.get("reasoning_steps", []):
                print(f"\n步骤 {step['step_number']}: {step['step_name']}")
                print(f"  内容: {step['content']}")
            
            # 如果启用反思，显示反思结果
            if enable_reflection and result.get("reflection_results"):
                print("\n反思结果：")
                for reflection in result.get("reflection_results", []):
                    print(f"\n步骤 {reflection['step']} 的质量评估：")
                    print(f"  质量分数: {reflection['quality_score']}/10")
                    if reflection.get("issues"):
                        print(f"  问题: {', '.join(reflection['issues'])}")
                    if reflection.get("strengths"):
                        print(f"  优点: {', '.join(reflection['strengths'])}")
                    if reflection.get("improvement_suggestions"):
                        print(f"  改进建议: {', '.join(reflection['improvement_suggestions'])}")
            
            print(f"\n最终答案：{result.get('final_answer', '未生成')}")
            print("-" * 60)


if __name__ == "__main__":
    demo_cot_with_reflection()
