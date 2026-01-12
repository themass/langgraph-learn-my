#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LangGraph 节点生命周期事件示例
演示如何正确获取和处理节点的生命周期事件
"""

from typing import TypedDict, List, Dict, Any, Optional, Union
import time

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage
from langchain_core.callbacks import BaseCallbackHandler
from langgraph.graph import StateGraph, END

# ===========================================================
# 状态定义
# ===========================================================

class NodeState(TypedDict):
    """节点状态定义"""
    messages: List[Union[HumanMessage, AIMessage, SystemMessage]]
    current_step: Optional[str]
    step_count: Optional[int]

def initialize_state() -> NodeState:
    """初始化状态"""
    return {
        "messages": [
            SystemMessage(content="你是一个有用的AI助手。")
        ],
        "current_step": None,
        "step_count": 0
    }

# ===========================================================
# 节点函数
# ===========================================================

def step1_node(state: NodeState) -> NodeState:
    """步骤1节点"""
    print("🔄 执行步骤1...")
    time.sleep(1)  # 模拟处理时间
    
    return {
        **state,
        "current_step": "step1",
        "step_count": state.get("step_count", 0) + 1
    }

def step2_node(state: NodeState) -> NodeState:
    """步骤2节点"""
    print("🔄 执行步骤2...")
    time.sleep(1.5)  # 模拟处理时间
    
    return {
        **state,
        "current_step": "step2",
        "step_count": state.get("step_count", 0) + 1
    }

def step3_node(state: NodeState) -> NodeState:
    """步骤3节点"""
    print("🔄 执行步骤3...")
    time.sleep(0.8)  # 模拟处理时间
    
    # 添加用户消息
    new_messages = state["messages"].copy()
    new_messages.append(HumanMessage(content="测试消息"))
    new_messages.append(AIMessage(content="这是步骤3的回复"))
    
    return {
        **state,
        "messages": new_messages,
        "current_step": "step3",
        "step_count": state.get("step_count", 0) + 1
    }

# ===========================================================
# 详细事件回调处理器
# ===========================================================

class DetailedCallbackHandler(BaseCallbackHandler):
    """详细事件回调处理器"""
    
    def __init__(self):
        super().__init__()
        self.events = []
        self.node_execution_order = []
    
    def on_chain_start(self, serialized: dict, inputs: dict, **kwargs):
        """链开始事件"""
        # 修复：处理 serialized 可能为 None 的情况
        if serialized is None:
            serialized = {}
        
        # 尝试从不同来源获取节点名称
        node_name = serialized.get("name", "unknown")
        if node_name == "unknown" and "name" in kwargs:
            node_name = kwargs["name"]
        
        event = {
            "event": "on_chain_start",
            "name": node_name,
            "inputs": inputs,
            "timestamp": time.time(),
            "node_id": serialized.get("id", "unknown"),
            "node_type": serialized.get("type", "unknown")
        }
        self.events.append(event)
        self.node_execution_order.append(f"开始: {node_name}")
        
        print(f"🟢 节点开始: {node_name}")
        print(f"   输入: {list(inputs.keys()) if isinstance(inputs, dict) else 'N/A'}")
        print(f"   节点ID: {event['node_id']}")
        print(f"   节点类型: {event['node_type']}")
    
    def on_chain_end(self, outputs: dict, **kwargs):
        """链结束事件"""
        serialized = kwargs.get("serialized", {})
        if serialized is None:
            serialized = {}
        
        # 调试：打印所有可用的信息
        print(f"🔍 DEBUG - on_chain_end kwargs keys: {list(kwargs.keys())}")
        print(f"🔍 DEBUG - serialized keys: {list(serialized.keys()) if isinstance(serialized, dict) else 'N/A'}")
        
        # 尝试从多个来源获取节点名称
        node_name = "unknown"
        
        # 方法1: 从 serialized 获取
        if isinstance(serialized, dict):
            node_name = serialized.get("name", node_name)
        
        # 方法2: 从 kwargs 直接获取
        if node_name == "unknown" and "name" in kwargs:
            node_name = kwargs["name"]
        
        # 方法3: 从 tags 获取
        if node_name == "unknown" and "tags" in kwargs:
            tags = kwargs["tags"]
            if isinstance(tags, list) and len(tags) > 0:
                node_name = tags[0]
        
        # 方法4: 从 metadata 获取
        if node_name == "unknown" and "metadata" in kwargs:
            metadata = kwargs["metadata"]
            if isinstance(metadata, dict) and "name" in metadata:
                node_name = metadata["name"]
        
        # 方法5: 从 outputs 推断（如果包含当前步骤信息）
        if node_name == "unknown" and isinstance(outputs, dict):
            current_step = outputs.get("current_step")
            if current_step:
                node_name = current_step
        
        event = {
            "event": "on_chain_end",
            "name": node_name,
            "outputs": outputs,
            "timestamp": time.time(),
            "node_id": serialized.get("id", "unknown"),
            "node_type": serialized.get("type", "unknown")
        }
        self.events.append(event)
        self.node_execution_order.append(f"结束: {node_name}")
        
        print(f"🔴 节点结束: {node_name}")
        print(f"   输出: {list(outputs.keys()) if isinstance(outputs, dict) else 'N/A'}")
        if isinstance(outputs, dict):
            for key, value in outputs.items():
                if isinstance(value, str) and len(value) > 50:
                    print(f"   {key}: {value[:50]}...")
                else:
                    print(f"   {key}: {value}")
    
    def on_chain_error(self, error: Exception, **kwargs):
        """链错误事件"""
        serialized = kwargs.get("serialized", {})
        node_name = serialized.get("name", "unknown")
        event = {
            "event": "on_chain_error",
            "name": node_name,
            "error": str(error),
            "timestamp": time.time(),
            "node_id": serialized.get("id", "unknown"),
            "node_type": serialized.get("type", "unknown")
        }
        self.events.append(event)
        self.node_execution_order.append(f"错误: {node_name}")
        
        print(f"🔴 节点错误: {node_name}")
        print(f"   错误: {error}")
    
    def get_events(self):
        """获取所有事件"""
        return self.events
    
    def get_execution_order(self):
        """获取执行顺序"""
        return self.node_execution_order
    
    def get_node_statistics(self):
        """获取节点统计信息"""
        stats = {}
        for event in self.events:
            node_name = event["name"]
            if node_name not in stats:
                stats[node_name] = {
                    "starts": 0,
                    "ends": 0,
                    "errors": 0,
                    "total_time": 0
                }
            
            if event["event"] == "on_chain_start":
                stats[node_name]["starts"] += 1
            elif event["event"] == "on_chain_end":
                stats[node_name]["ends"] += 1
            elif event["event"] == "on_chain_error":
                stats[node_name]["errors"] += 1
        
        return stats

# ===========================================================
# 图创建
# ===========================================================

def create_node_lifecycle_graph():
    """创建节点生命周期图"""
    workflow = StateGraph(NodeState)
    
    workflow.add_node("step1", step1_node)
    workflow.add_node("step2", step2_node)
    workflow.add_node("step3", step3_node)
    
    workflow.add_edge("step1", "step2")
    workflow.add_edge("step2", "step3")
    workflow.add_edge("step3", END)
    
    workflow.set_entry_point("step1")
    
    return workflow.compile()

# ===========================================================
# 示例函数
# ===========================================================

def example_1_basic_lifecycle():
    """示例1: 基本节点生命周期"""
    print("\n===== 示例1: 基本节点生命周期 =====")
    
    graph = create_node_lifecycle_graph()
    state = initialize_state()
    
    # 创建回调处理器
    callback_handler = DetailedCallbackHandler()
    
    config = {
        "callbacks": [callback_handler]
    }
    
    print("开始执行图...")
    print("=" * 50)
    
    # 执行图
    result = graph.invoke(state, config)
    
    print("=" * 50)
    print("执行完成!")
    print(f"最终状态: {result}")
    
    return callback_handler

def example_2_stream_with_lifecycle():
    """示例2: 流式处理 + 生命周期事件"""
    print("\n===== 示例2: 流式处理 + 生命周期事件 =====")
    
    graph = create_node_lifecycle_graph()
    state = initialize_state()
    
    # 创建回调处理器
    callback_handler = DetailedCallbackHandler()
    
    config = {
        "callbacks": [callback_handler]
    }
    
    print("开始流式处理...")
    print("=" * 50)
    
    # 流式处理
    events = graph.stream(state, config, stream_mode="values")
    
    print("\n=== 状态更新 ===")
    for i, event in enumerate(events):
        print(f"\n状态更新 #{i+1}:")
        print(f"  当前步骤: {event.get('current_step', 'N/A')}")
        print(f"  步骤计数: {event.get('step_count', 'N/A')}")
        print(f"  消息数量: {len(event.get('messages', []))}")
    
    print("\n=== 节点生命周期事件 ===")
    events = callback_handler.get_events()
    for i, event in enumerate(events):
        print(f"\n事件 #{i+1}:")
        print(f"  事件类型: {event['event']}")
        print(f"  节点名称: {event['name']}")
        print(f"  节点ID: {event['node_id']}")
        print(f"  节点类型: {event['node_type']}")
        print(f"  时间戳: {event['timestamp']}")
    
    return callback_handler

def example_3_detailed_analysis():
    """示例3: 详细分析"""
    print("\n===== 示例3: 详细分析 =====")
    
    # 使用示例2的结果
    callback_handler = example_2_stream_with_lifecycle()
    
    print("\n=== 执行顺序 ===")
    execution_order = callback_handler.get_execution_order()
    for i, step in enumerate(execution_order):
        print(f"{i+1}. {step}")
    
    print("\n=== 节点统计 ===")
    stats = callback_handler.get_node_statistics()
    for node_name, node_stats in stats.items():
        print(f"\n节点: {node_name}")
        print(f"  开始次数: {node_stats['starts']}")
        print(f"  结束次数: {node_stats['ends']}")
        print(f"  错误次数: {node_stats['errors']}")
        print(f"  成功率: {node_stats['ends'] / max(node_stats['starts'], 1) * 100:.1f}%")
    
    print("\n=== 事件时间线 ===")
    events = callback_handler.get_events()
    if events:
        start_time = events[0]["timestamp"]
        for event in events:
            relative_time = event["timestamp"] - start_time
            print(f"{relative_time:.2f}s - {event['event']} - {event['name']}")

# ===========================================================
# 主函数
# ===========================================================

if __name__ == "__main__":
    print("===== LangGraph 节点生命周期事件示例 =====")
    print("演示如何正确获取和处理节点的生命周期事件\n")
    
    try:
        # 示例1: 基本节点生命周期
        example_1_basic_lifecycle()
        input("\n按Enter继续...")
        
        # 示例2: 流式处理 + 生命周期事件
        example_2_stream_with_lifecycle()
        input("\n按Enter继续...")
        
        # 示例3: 详细分析
        example_3_detailed_analysis()
        
        print("\n===== 总结 =====")
        print("✅ 成功获取了节点的完整生命周期事件")
        print("✅ 包括开始、结束、错误等事件类型")
        print("✅ 获取了节点ID、类型、输入输出等详细信息")
        print("✅ 可以分析执行顺序、统计信息和时间线")
        print("✅ 回调处理器是获取事件类型信息的正确方式")
        
    except Exception as e:
        print(f"执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
