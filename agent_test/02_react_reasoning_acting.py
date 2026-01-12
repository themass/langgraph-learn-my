#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ReAct (Reasoning + Acting) 推理与行动范式
==========================================

核心思想：结合推理和行动，形成 Think-Act-Observe 循环，使智能体能够与环境交互。

特点：
- 思考(Think)：分析当前状态，决定下一步行动
- 行动(Act)：执行选定的行动
- 观察(Observe)：观察行动结果，更新状态
- 循环直到任务完成
"""

from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from utils import get_llm
from log_utils import log_node_input, log_node_output, log_prompt
from prompts.react_prompts import (
    REACT_SYSTEM_PROMPT,
    format_think_prompt,
    format_finish_prompt
)
import json


# =================================================================
# 工具定义
# =================================================================

class Tool:
    """简单工具定义"""
    def __init__(self, name: str, description: str, func: callable):
        self.name = name
        self.description = description
        self.func = func
    
    def execute(self, **kwargs):
        return self.func(**kwargs)


# 示例工具
def search_tool(query: str) -> str:
    """搜索工具"""
    # 模拟搜索结果
    results = {
        "Python": "Python是一种高级编程语言，广泛用于数据科学和AI。",
        "LangGraph": "LangGraph是用于构建状态机工作流的框架。",
        "ReAct": "ReAct是结合推理和行动的智能体模式。"
    }
    return results.get(query, f"未找到关于'{query}'的信息")


def calculate_tool(expression: str) -> str:
    """计算工具"""
    try:
        result = eval(expression)
        return f"计算结果：{result}"
    except Exception as e:
        return f"计算错误：{str(e)}"


def get_time_tool() -> str:
    """获取时间工具"""
    from datetime import datetime
    return f"当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


# 可用工具列表
AVAILABLE_TOOLS = {
    "search": Tool("search", "搜索信息", lambda query: search_tool(query)),
    "calculate": Tool("calculate", "执行数学计算", lambda expression: calculate_tool(expression)),
    "get_time": Tool("get_time", "获取当前时间", lambda: get_time_tool())
}


# =================================================================
# 状态定义
# =================================================================

class ReActState(TypedDict):
    """ReAct 状态"""
    task: str  # 任务描述
    thought: Optional[str]  # 当前思考
    action: Optional[str]  # 当前行动
    action_input: Optional[str]  # 行动输入
    observation: Optional[str]  # 观察结果
    history: List[Dict[str, str]]  # 历史记录
    final_answer: Optional[str]  # 最终答案
    finished: bool  # 是否完成


# =================================================================
# 节点函数
# =================================================================

def think_node(state: ReActState) -> Dict[str, Any]:
    """思考节点 - 分析当前状态，决定下一步行动"""
    
    task = state["task"]
    history = state.get("history", [])
    observation = state.get("observation", "")
    
    # 构建历史记录
    history_text = ""
    for i, entry in enumerate(history[-3:], 1):  # 只显示最近3条
        history_text += f"\n{i}. {entry.get('type', 'unknown')}: {entry.get('content', '')}"
    
    llm = get_llm(temperature=0.3)
    
    # 构建工具描述
    tools_desc = "\n".join([f"- {name}: {tool.description}" for name, tool in AVAILABLE_TOOLS.items()])
    
    # 使用 prompt 模板
    human_prompt = format_think_prompt(
        task=task,
        observation=observation if observation else "无",
        history_text=history_text if history_text else "无",
        tools_desc=tools_desc
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", REACT_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    # 记录完整的 prompt
    log_prompt("think_node", [
        ("system", REACT_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析结果
    try:
        import re
        json_str = re.search(r'\{.*\}', result.content, re.DOTALL)
        if json_str:
            decision = json.loads(json_str.group())
        else:
            decision = {"thought": result.content, "action": "finish", "action_input": "", "reasoning": ""}
    except:
        decision = {"thought": result.content, "action": "finish", "action_input": "", "reasoning": ""}
    
    # 更新历史
    history = state.get("history", [])
    history.append({
        "type": "Thought",
        "content": decision.get("thought", "")
    })
    
    output = {
        "thought": decision.get("thought", ""),
        "action": decision.get("action", "finish"),
        "action_input": decision.get("action_input", ""),
        "history": history
    }
    
    log_node_output("think_node", output)
    
    return output


def act_node(state: ReActState) -> Dict[str, Any]:
    """行动节点 - 执行选定的行动"""
    
    log_node_input("act_node", state)
    
    action = state.get("action", "finish")
    action_input = state.get("action_input", "")
    
    if action == "finish":
        return {"observation": "任务完成"}
    
    # 执行工具
    if action in AVAILABLE_TOOLS:
        tool = AVAILABLE_TOOLS[action]
        try:
            if action_input:
                observation = tool.execute(**{"query": action_input} if action == "search" 
                                         else {"expression": action_input} if action == "calculate"
                                         else {})
            else:
                observation = tool.execute()
        except Exception as e:
            observation = f"执行错误：{str(e)}"
    else:
        observation = f"未知行动：{action}"
    
    # 更新历史
    history = state.get("history", [])
    history.append({
        "type": "Action",
        "content": f"{action}({action_input})"
    })
    history.append({
        "type": "Observation",
        "content": observation
    })
    
    output = {
        "observation": observation,
        "history": history
    }
    
    log_node_output("act_node", output)
    
    return output


def should_continue(state: ReActState) -> str:
    """判断是否继续"""
    action = state.get("action", "finish")
    
    if action == "finish":
        return "finish"
    
    # 检查是否达到最大迭代次数
    history = state.get("history", [])
    if len(history) >= 20:  # 最多10轮（每轮2条记录：thought + action/observation）
        return "finish"
    
    return "think"


def finish_node(state: ReActState) -> Dict[str, Any]:
    """完成节点 - 生成最终答案"""
    
    log_node_input("finish_node", state)
    
    task = state["task"]
    history = state.get("history", [])
    
    # 构建完整历史
    history_text = ""
    for entry in history:
        history_text += f"\n{entry.get('type', '')}: {entry.get('content', '')}"
    
    llm = get_llm(temperature=0.3)
    
    # 使用 prompt 模板
    human_prompt = format_finish_prompt(task=task, history_text=history_text)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", REACT_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    # 记录完整的 prompt
    log_prompt("finish_node", [
        ("system", REACT_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析结果
    try:
        import re
        json_str = re.search(r'\{.*\}', result.content, re.DOTALL)
        if json_str:
            answer = json.loads(json_str.group())
        else:
            answer = {"final_answer": result.content, "summary": ""}
    except:
        answer = {"final_answer": result.content, "summary": ""}
    
    output = {
        "final_answer": answer.get("final_answer", result.content),
        "finished": True
    }
    
    log_node_output("finish_node", output)
    
    return output


# =================================================================
# 构建图
# =================================================================

def create_react_graph():
    """创建 ReAct 图"""
    
    graph = StateGraph(ReActState)
    
    # 添加节点
    graph.add_node("think", think_node)
    graph.add_node("act", act_node)
    graph.add_node("finish", finish_node)
    
    # 添加边
    graph.set_entry_point("think")
    graph.add_edge("think", "act")
    graph.add_conditional_edges(
        "act",
        should_continue,
        {
            "think": "think",  # 继续思考
            "finish": "finish"  # 完成任务
        }
    )
    graph.add_edge("finish", END)
    
    return graph.compile()


# =================================================================
# Demo 示例
# =================================================================

def demo_react():
    """ReAct Demo"""
    
    print("=" * 60)
    print("ReAct (Reasoning + Acting) 推理与行动 Demo")
    print("=" * 60)
    
    # 创建图
    graph = create_react_graph()
    
    # 测试任务
    test_tasks = [
        "搜索'Python'的信息，然后计算 2+3 等于多少",
        # "获取当前时间，然后搜索'LangGraph'的信息"
    ]
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n【任务 {i}】")
        print(f"任务：{task}\n")
        
        # 运行代理
        initial_state = {
            "task": task,
            "thought": None,
            "action": None,
            "action_input": None,
            "observation": None,
            "history": [],
            "final_answer": None,
            "finished": False
        }
        
        result = graph.invoke(initial_state)
        
        # 显示结果
        print("执行过程：")
        for entry in result["history"]:
            print(f"  {entry['type']}: {entry['content']}")
        
        print(f"\n最终答案：{result['final_answer']}")
        print("-" * 60)


if __name__ == "__main__":
    demo_react()
