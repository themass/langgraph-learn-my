#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tree of Thoughts (ToT) 思维树范式
==================================

核心思想：探索多个推理路径，构建搜索树，通过评估和选择最优路径来解决问题。

特点：
- 生成多个候选推理路径
- 评估每个路径的质量
- 选择最优路径继续扩展
- 适用于需要探索多种可能性的问题
"""

from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from utils import get_llm
from log_utils import log_node_input, log_node_output, log_prompt
from prompts.tot_prompts import (
    TOT_SYSTEM_PROMPT,
    format_generate_prompt,
    format_evaluate_prompt,
    format_expand_prompt
)
import json


# =================================================================
# 状态定义
# =================================================================

class ToTState(TypedDict):
    """ToT 状态"""
    question: str  # 原始问题
    paths: List[Dict[str, Any]]  # 所有路径
    current_path_id: Optional[int]  # 当前选择的路径ID
    depth: int  # 搜索深度
    best_answer: Optional[str]  # 最佳答案
    finished: bool  # 是否完成


# =================================================================
# 节点函数
# =================================================================

def generate_paths_node(state: ToTState) -> Dict[str, Any]:
    """生成候选路径节点"""
    
    question = state["question"]
    existing_paths = state.get("paths", [])
    depth = state.get("depth", 0)
    
    # 构建已有路径信息
    paths_text = ""
    if existing_paths:
        for path in existing_paths[-3:]:  # 只显示最近3条
            paths_text += f"\n路径{path.get('path_id', '?')}: {path.get('direction', '')}"
    
    llm = get_llm(temperature=0.7)  # 较高温度以增加多样性
    
    # 使用 prompt 模板
    human_prompt = format_generate_prompt(
        question=question,
        current_state=f"深度 {depth}",
        existing_paths=paths_text if paths_text else "无"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", TOT_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    # 记录完整的 prompt
    log_prompt("generate_paths_node", [
        ("system", TOT_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析结果
    try:
        import re
        json_str = re.search(r'\{.*\}', result.content, re.DOTALL)
        if json_str:
            paths_data = json.loads(json_str.group())
            new_paths = paths_data.get("paths", [])
        else:
            # 如果解析失败，创建默认路径
            new_paths = [{
                "path_id": len(existing_paths) + 1,
                "direction": "直接推理路径",
                "steps": ["分析问题", "逐步推理", "得出结论"],
                "assumptions": []
            }]
    except Exception as e:
        new_paths = [{
            "path_id": len(existing_paths) + 1,
            "direction": f"路径 {len(existing_paths) + 1}",
            "steps": ["分析问题", "逐步推理", "得出结论"],
            "assumptions": []
        }]
    
    # 为每个新路径分配ID
    next_id = len(existing_paths) + 1
    for path in new_paths:
        path["path_id"] = next_id
        path["depth"] = depth
        next_id += 1
    
    all_paths = existing_paths + new_paths
    
    output = {
        "paths": all_paths
    }
    
    log_node_output("generate_paths_node", output)
    
    return output


def evaluate_paths_node(state: ToTState) -> Dict[str, Any]:
    """评估路径节点"""
    
    log_node_input("evaluate_paths_node", state)
    
    question = state["question"]
    paths = state.get("paths", [])
    
    if not paths:
        return {"best_answer": "无法生成路径", "finished": True}
    
    # 只评估最近的路径（当前深度生成的）
    current_depth = state.get("depth", 0)
    paths_to_evaluate = [p for p in paths if p.get("depth", 0) == current_depth]
    
    if not paths_to_evaluate:
        paths_to_evaluate = paths[-5:]  # 评估最近5条
    
    # 构建路径描述
    paths_text = ""
    for path in paths_to_evaluate:
        paths_text += f"\n路径{path['path_id']}:\n"
        paths_text += f"  方向: {path.get('direction', '')}\n"
        paths_text += f"  步骤: {', '.join(path.get('steps', []))}\n"
    
    llm = get_llm(temperature=0.3)
    
    # 使用 prompt 模板
    human_prompt = format_evaluate_prompt(
        question=question,
        paths=paths_text
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", TOT_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    # 记录完整的 prompt
    log_prompt("evaluate_paths_node", [
        ("system", TOT_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析结果
    try:
        import re
        json_str = re.search(r'\{.*\}', result.content, re.DOTALL)
        if json_str:
            eval_data = json.loads(json_str.group())
            best_path_id = eval_data.get("best_path_id")
            evaluations = eval_data.get("evaluations", [])
        else:
            # 默认选择第一条路径
            best_path_id = paths_to_evaluate[0]["path_id"] if paths_to_evaluate else None
            evaluations = []
    except:
        best_path_id = paths_to_evaluate[0]["path_id"] if paths_to_evaluate else None
        evaluations = []
    
    # 更新路径的评估信息
    for eval_item in evaluations:
        path_id = eval_item.get("path_id")
        for path in paths:
            if path["path_id"] == path_id:
                path["score"] = eval_item.get("score", 0)
                path["evaluation"] = eval_item.get("reasoning", "")
                break
    
    output = {
        "paths": paths,
        "current_path_id": best_path_id
    }
    
    log_node_output("evaluate_paths_node", output)
    
    return output


def expand_path_node(state: ToTState) -> Dict[str, Any]:
    """扩展路径节点 - 基于最佳路径继续推理"""
    
    log_node_input("expand_path_node", state)
    
    question = state["question"]
    paths = state.get("paths", [])
    current_path_id = state.get("current_path_id")
    depth = state.get("depth", 0)
    
    if not current_path_id:
        return {"best_answer": "无法确定最佳路径", "finished": True}
    
    # 找到当前路径
    current_path = None
    for path in paths:
        if path["path_id"] == current_path_id:
            current_path = path
            break
    
    if not current_path:
        return {"best_answer": "路径不存在", "finished": True}
    
    llm = get_llm(temperature=0.3)
    
    # 使用 prompt 模板
    human_prompt = format_expand_prompt(
        question=question,
        direction=current_path.get('direction', ''),
        steps=', '.join(current_path.get('steps', []))
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", TOT_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    # 记录完整的 prompt
    log_prompt("expand_path_node", [
        ("system", TOT_SYSTEM_PROMPT),
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
            answer = answer_data.get("answer", result.content)
        else:
            answer = result.content
    except:
        answer = result.content
    
    output = {
        "best_answer": answer,
        "depth": depth + 1
    }
    
    log_node_output("expand_path_node", output)
    
    return output


def should_continue_search(state: ToTState) -> str:
    """判断是否继续搜索"""
    depth = state.get("depth", 0)
    best_answer = state.get("best_answer")
    
    # 如果已有答案或深度过深，则完成
    if best_answer or depth >= 3:
        return "finish"
    
    return "expand"


# =================================================================
# 构建图
# =================================================================

def create_tot_graph():
    """创建 ToT 图"""
    
    graph = StateGraph(ToTState)
    
    # 添加节点
    graph.add_node("generate", generate_paths_node)
    graph.add_node("evaluate", evaluate_paths_node)
    graph.add_node("expand", expand_path_node)
    
    # 添加边
    graph.set_entry_point("generate")
    graph.add_edge("generate", "evaluate")
    graph.add_edge("evaluate", "expand")
    graph.add_conditional_edges(
        "expand",
        should_continue_search,
        {
            "expand": "generate",  # 继续生成新路径
            "finish": END  # 完成
        }
    )
    
    return graph.compile()


# =================================================================
# Demo 示例
# =================================================================

def demo_tot():
    """ToT Demo"""
    
    print("=" * 60)
    print("Tree of Thoughts (ToT) 思维树 Demo")
    print("=" * 60)
    
    # 创建图
    graph = create_tot_graph()
    
    # 测试问题
    test_questions = [
        "如何提高团队的工作效率？",
        "设计一个用户友好的登录系统需要考虑哪些因素？"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n【问题 {i}】")
        print(f"问题：{question}\n")
        
        # 运行搜索
        initial_state = {
            "question": question,
            "paths": [],
            "current_path_id": None,
            "depth": 0,
            "best_answer": None,
            "finished": False
        }
        
        result = graph.invoke(initial_state)
        
        # 显示结果
        print("生成的路径：")
        for path in result.get("paths", []):
            print(f"\n路径{path['path_id']}: {path.get('direction', '')}")
            print(f"  步骤: {', '.join(path.get('steps', []))}")
            if path.get('score') is not None:
                print(f"  评分: {path['score']}/10")
        
        if result.get("current_path_id"):
            print(f"\n选择的最佳路径: 路径{result['current_path_id']}")
        
        print(f"\n最终答案：{result.get('best_answer', '未找到答案')}")
        print("-" * 60)


if __name__ == "__main__":
    demo_tot()
