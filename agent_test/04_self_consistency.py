#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Self-Consistency 自我一致性范式
================================

核心思想：生成多个推理路径，通过多数投票或一致性评估来选择最可靠的答案。

特点：
- 生成多个独立的推理路径
- 评估答案的一致性
- 选择最一致的答案
- 适用于需要高可靠性的问题
"""

from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from collections import Counter
from utils import get_llm
from log_utils import log_node_input, log_node_output, log_prompt
from prompts.self_consistency_prompts import (
    SELF_CONSISTENCY_SYSTEM_PROMPT,
    format_generate_prompt as format_sc_generate_prompt,
    format_evaluate_prompt as format_sc_evaluate_prompt
)
import json


# =================================================================
# 状态定义
# =================================================================

class SelfConsistencyState(TypedDict):
    """Self-Consistency 状态"""
    question: str  # 原始问题
    reasoning_paths: List[Dict[str, Any]]  # 多个推理路径
    answers: List[str]  # 所有答案
    final_answer: Optional[str]  # 最终答案
    consistency_score: Optional[float]  # 一致性分数
    finished: bool  # 是否完成


# =================================================================
# 节点函数
# =================================================================

def generate_reasoning_path_node(state: SelfConsistencyState) -> Dict[str, Any]:
    """生成单个推理路径节点"""
    
    log_node_input("generate_reasoning_path_node", state)
    
    question = state["question"]
    existing_paths = state.get("reasoning_paths", [])
    path_number = len(existing_paths) + 1
    
    # 使用不同的温度生成多样化的推理
    temperatures = [0.3, 0.5, 0.7, 0.5, 0.3]  # 5个路径的温度分布
    temperature = temperatures[min(path_number - 1, len(temperatures) - 1)]
    
    llm = get_llm(temperature=temperature)
    
    # 使用 prompt 模板
    human_prompt = format_sc_generate_prompt(question=question)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SELF_CONSISTENCY_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    # 记录完整的 prompt
    log_prompt("generate_reasoning_path_node", [
        ("system", SELF_CONSISTENCY_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析结果
    try:
        import re
        json_str = re.search(r'\{.*\}', result.content, re.DOTALL)
        if json_str:
            path_data = json.loads(json_str.group())
        else:
            path_data = {
                "reasoning": result.content,
                "answer": result.content.split("\n")[-1] if "\n" in result.content else result.content,
                "confidence": "中",
                "key_points": []
            }
    except:
        path_data = {
            "reasoning": result.content,
            "answer": result.content.split("\n")[-1] if "\n" in result.content else result.content,
            "confidence": "中",
            "key_points": []
        }
    
    new_path = {
        "path_id": path_number,
        "reasoning": path_data.get("reasoning", ""),
        "answer": path_data.get("answer", ""),
        "confidence": path_data.get("confidence", "中"),
        "key_points": path_data.get("key_points", [])
    }
    
    reasoning_paths = existing_paths + [new_path]
    answers = [p["answer"] for p in reasoning_paths]
    
    output = {
        "reasoning_paths": reasoning_paths,
        "answers": answers
    }
    
    log_node_output("generate_reasoning_path_node", output)
    
    return output


def evaluate_consistency_node(state: SelfConsistencyState) -> Dict[str, Any]:
    """评估一致性节点"""
    
    log_node_input("evaluate_consistency_node", state)
    
    reasoning_paths = state.get("reasoning_paths", [])
    answers = state.get("answers", [])
    
    if not answers:
        return {"final_answer": "无法生成答案", "finished": True}
    
    # 统计答案频率
    answer_counter = Counter(answers)
    
    # 找到最频繁的答案
    most_common_answer, count = answer_counter.most_common(1)[0]
    total = len(answers)
    consistency_score = count / total
    
    # 如果一致性不够高，尝试语义相似度评估
    if consistency_score < 0.6 and len(reasoning_paths) >= 3:
        # 使用LLM评估语义一致性
        llm = get_llm(temperature=0.3)
        
        answers_text = "\n".join([f"{i+1}. {ans}" for i, ans in enumerate(answers)])
        
        json_example = """{{
    "most_consistent_answer": "最一致的答案",
    "consistency_reasoning": "一致性评估理由",
    "consistency_score": 0-1之间的一致性分数
}}"""
        
        human_prompt = """以下是同一个问题的多个答案：

{answers_text}

请评估这些答案的一致性，并选择最可靠的答案。返回JSON格式：
{json_example}""".format(answers_text=answers_text, json_example=json_example)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", SELF_CONSISTENCY_SYSTEM_PROMPT),
            ("human", human_prompt)
        ])
        
        # 记录完整的 prompt
        log_prompt("evaluate_consistency_node", [
            ("system", SELF_CONSISTENCY_SYSTEM_PROMPT),
            ("human", human_prompt)
        ])
        
        chain = prompt | llm
        result = chain.invoke({})
        
        try:
            import re
            json_str = re.search(r'\{.*\}', result.content, re.DOTALL)
            if json_str:
                eval_data = json.loads(json_str.group())
                final_answer = eval_data.get("most_consistent_answer", most_common_answer)
                consistency_score = eval_data.get("consistency_score", consistency_score)
            else:
                final_answer = most_common_answer
        except:
            final_answer = most_common_answer
    else:
        final_answer = most_common_answer
    
    output = {
        "final_answer": final_answer,
        "consistency_score": consistency_score
    }
    
    log_node_output("evaluate_consistency_node", output)
    
    return output


def should_generate_more(state: SelfConsistencyState) -> str:
    """判断是否需要生成更多路径"""
    reasoning_paths = state.get("reasoning_paths", [])
    consistency_score = state.get("consistency_score")
    
    # 如果已经有5个路径，或者一致性很高，则完成
    if len(reasoning_paths) >= 5:
        return "evaluate"
    
    # 如果一致性很高（>0.8），也可以完成
    if consistency_score and consistency_score > 0.8:
        return "evaluate"
    
    return "generate"


# =================================================================
# 构建图
# =================================================================

def create_self_consistency_graph():
    """创建 Self-Consistency 图"""
    
    graph = StateGraph(SelfConsistencyState)
    
    # 添加节点
    graph.add_node("generate", generate_reasoning_path_node)
    graph.add_node("evaluate", evaluate_consistency_node)
    
    # 添加边
    graph.set_entry_point("generate")
    graph.add_conditional_edges(
        "generate",
        should_generate_more,
        {
            "generate": "generate",  # 继续生成
            "evaluate": "evaluate"  # 评估一致性
        }
    )
    graph.add_edge("evaluate", END)
    
    return graph.compile()


# =================================================================
# Demo 示例
# =================================================================

def demo_self_consistency():
    """Self-Consistency Demo"""
    
    print("=" * 60)
    print("Self-Consistency 自我一致性 Demo")
    print("=" * 60)
    
    # 创建图
    graph = create_self_consistency_graph()
    
    # 测试问题
    test_questions = [
        "如果一个数的平方是16，这个数是多少？",
        "如何提高学习效率？请给出3个建议。"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n【问题 {i}】")
        print(f"问题：{question}\n")
        
        # 运行推理
        initial_state = {
            "question": question,
            "reasoning_paths": [],
            "answers": [],
            "final_answer": None,
            "consistency_score": None,
            "finished": False
        }
        
        result = graph.invoke(initial_state)
        
        # 显示结果
        print("生成的推理路径：")
        for path in result.get("reasoning_paths", []):
            print(f"\n路径 {path['path_id']}:")
            print(f"  推理: {path.get('reasoning', '')[:100]}...")
            print(f"  答案: {path.get('answer', '')}")
            print(f"  信心: {path.get('confidence', '')}")
        
        print(f"\n答案统计:")
        answer_counter = Counter(result.get("answers", []))
        for answer, count in answer_counter.most_common():
            print(f"  '{answer}': {count}次")
        
        print(f"\n一致性分数: {result.get('consistency_score', 0):.2%}")
        print(f"最终答案: {result.get('final_answer', '未确定')}")
        print("-" * 60)


if __name__ == "__main__":
    demo_self_consistency()
