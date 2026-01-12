#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LangGraph 时间旅行示例
===================
本示例演示LangGraph的检查点功能，包括:
1. 状态检查点保存
2. 状态回放与分支执行
3. 时间旅行调试

WHY - 设计思路:
1. 复杂对话流程需要可追溯性和可调试能力
2. 用户可能需要从历史状态重新开始对话
3. 开发者需要分析执行路径和状态变化
4. 支持"假设如果"的场景模拟

HOW - 实现方式:
1. 使用MemorySaver保存状态检查点
2. 通过thread_id管理不同的对话线程
3. 实现状态回放和分支执行功能
4. 提供时间旅行调试工具

WHAT - 功能作用:
通过本示例，你将学习如何使用LangGraph的检查点功能
实现状态回放、分支执行和时间旅行调试
"""

from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import OllamaLLM
import json
import time

# ===========================================================
# 第1部分: 状态定义
# ===========================================================

class TimeTravelState(TypedDict):
    """时间旅行状态定义"""
    messages: List[HumanMessage | AIMessage | SystemMessage]  # 对话历史
    current_step: str  # 当前执行步骤
    step_count: int  # 步骤计数
    metadata: Dict[str, Any]  # 元数据

# ===========================================================
# 第2部分: 节点函数
# ===========================================================

def get_llm():
    """获取LLM实例"""
    return OllamaLLM(
        model="llama3",
        temperature=0.7,
    )

def step1_node(state: TimeTravelState) -> TimeTravelState:
    """步骤1: 分析用户输入"""
    print("🔄 执行步骤1: 分析用户输入")
    
    # 获取最后一条用户消息
    last_message = state["messages"][-1].content if state["messages"] else ""
    
    # 使用LLM分析输入
    llm = get_llm()
    analysis = llm.invoke(f"分析以下用户输入: {last_message}")
    
    # 更新状态
    new_state = state.copy()
    new_state["messages"].append(AIMessage(content=f"分析结果: {analysis}"))
    new_state["current_step"] = "step1"
    new_state["step_count"] += 1
    new_state["metadata"]["analysis"] = analysis
    
    return new_state

def step2_node(state: TimeTravelState) -> TimeTravelState:
    """步骤2: 生成回复"""
    print("🔄 执行步骤2: 生成回复")
    
    # 获取对话历史
    messages = state["messages"]
    
    # 使用LLM生成回复
    llm = get_llm()
    context = "\n".join([f"{'用户' if isinstance(m, HumanMessage) else 'AI'}: {m.content}" for m in messages[-3:]])
    
    response = llm.invoke(f"基于以下对话历史生成回复:\n{context}")
    
    # 更新状态
    new_state = state.copy()
    new_state["messages"].append(AIMessage(content=response))
    new_state["current_step"] = "step2"
    new_state["step_count"] += 1
    new_state["metadata"]["response"] = response
    
    return new_state

def step3_node(state: TimeTravelState) -> TimeTravelState:
    """步骤3: 总结对话"""
    print("🔄 执行步骤3: 总结对话")
    
    # 获取所有消息
    messages = state["messages"]
    
    # 使用LLM总结对话
    llm = get_llm()
    conversation = "\n".join([f"{'用户' if isinstance(m, HumanMessage) else 'AI'}: {m.content}" for m in messages])
    
    summary = llm.invoke(f"总结以下对话:\n{conversation}")
    
    # 更新状态
    new_state = state.copy()
    new_state["messages"].append(AIMessage(content=f"对话总结: {summary}"))
    new_state["current_step"] = "step3"
    new_state["step_count"] += 1
    new_state["metadata"]["summary"] = summary
    
    return new_state

# ===========================================================
# 第3部分: 图构建
# ===========================================================

def create_time_travel_graph():
    """创建支持时间旅行的图"""
    # 创建状态图
    workflow = StateGraph(TimeTravelState)
    
    # 添加节点
    workflow.add_node("step1", step1_node)
    workflow.add_node("step2", step2_node)
    workflow.add_node("step3", step3_node)
    
    # 设置边
    workflow.add_edge("step1", "step2")
    workflow.add_edge("step2", "step3")
    workflow.add_edge("step3", END)
    
    # 设置入口点
    workflow.set_entry_point("step1")
    
    # 创建检查点存储器
    memory = MemorySaver()
    
    # 编译图
    return workflow.compile(checkpointer=memory)

# ===========================================================
# 第4部分: 时间旅行功能
# ===========================================================

def initialize_state(user_input: str) -> TimeTravelState:
    """初始化状态"""
    return {
        "messages": [
            SystemMessage(content="这是一个支持时间旅行的对话系统。"),
            HumanMessage(content=user_input)
        ],
        "current_step": "start",
        "step_count": 0,
        "metadata": {}
    }

def run_conversation(app, thread_id: str, user_input: str):
    """运行对话"""
    print(f"\n=== 开始对话 (线程: {thread_id}) ===")
    
    # 初始化状态
    initial_state = initialize_state(user_input)
    
    # 执行图
    result = app.invoke(
        initial_state,
        config={"configurable": {"thread_id": thread_id}}
    )
    
    print("对话完成!")
    return result

def get_checkpoint_info(app, thread_id: str):
    """获取检查点信息"""
    try:
        checkpoint = app.get_state(
            config={"configurable": {"thread_id": thread_id}}
        )
        return checkpoint
    except Exception as e:
        print(f"获取检查点失败: {e}")
        return None

def print_checkpoint_info(checkpoint):
    """打印检查点信息"""
    if not checkpoint:
        return
    
    print("\n=== 检查点信息 ===")
    print(f"步骤数: {checkpoint.metadata.get('step', 'N/A')}")
    print(f"创建时间: {checkpoint.created_at}")
    print(f"配置: {checkpoint.config}")
    
    # 打印消息历史
    messages = checkpoint.values.get("messages", [])
    print(f"\n消息历史 ({len(messages)} 条):")
    for i, msg in enumerate(messages):
        msg_type = "用户" if isinstance(msg, HumanMessage) else "AI"
        print(f"  {i+1}. [{msg_type}] {msg.content[:50]}...")

def time_travel_demo():
    """时间旅行演示"""
    print("===== LangGraph 时间旅行示例 =====")
    
    # 创建图
    app = create_time_travel_graph()
    
    # 演示1: 正常对话流程
    print("\n1. 正常对话流程")
    thread_id_1 = "conversation-1"
    result1 = run_conversation(app, thread_id_1, "你好，请介绍一下自己")
    
    # 获取检查点信息
    checkpoint1 = get_checkpoint_info(app, thread_id_1)
    print_checkpoint_info(checkpoint1)
    
    # 演示2: 分支对话
    print("\n2. 分支对话 (从步骤1开始)")
    thread_id_2 = "conversation-2"
    
    # 重新开始对话，但使用不同的输入
    result2 = run_conversation(app, thread_id_2, "请告诉我今天的天气")
    
    # 获取检查点信息
    checkpoint2 = get_checkpoint_info(app, thread_id_2)
    print_checkpoint_info(checkpoint2)
    
    # 演示3: 状态比较
    print("\n3. 状态比较")
    if checkpoint1 and checkpoint2:
        print("两个对话的状态比较:")
        print(f"  对话1步骤数: {checkpoint1.metadata.get('step', 'N/A')}")
        print(f"  对话2步骤数: {checkpoint2.metadata.get('step', 'N/A')}")
        print(f"  对话1消息数: {len(checkpoint1.values.get('messages', []))}")
        print(f"  对话2消息数: {len(checkpoint2.values.get('messages', []))}")
    
    print("\n===== 时间旅行示例完成 =====")

# ===========================================================
# 第5部分: 主函数
# ===========================================================

def main():
    """主函数"""
    try:
        time_travel_demo()
    except Exception as e:
        print(f"执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
