#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""流式输出 - LangGraph流式处理与实时反馈示例（修复版）

修复的问题:
1. 添加了缺失的 BaseMessage 导入
2. 改进了异常处理，使用更具体的异常类型
3. 修复了 MockLLM 的 stream 方法返回格式
4. 改进了进度更新逻辑
5. 优化了 token 估算方法
"""

from typing import TypedDict, List, Dict, Any, Optional, Union, Literal
import time
import json
from datetime import datetime

# 修复1: 添加缺失的 BaseMessage 导入
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langgraph.graph import StateGraph, END
from langchain_core.callbacks import BaseCallbackHandler

# ===========================================================
# 第1部分: 状态定义
# ===========================================================

class StreamState(TypedDict):
    """流式处理状态定义"""
    messages: List[Union[HumanMessage, AIMessage, SystemMessage]]  # 消息历史
    current_response: Optional[str]  # 当前正在生成的响应
    thinking: Optional[str]  # 思考过程
    progress: Optional[float]  # 生成进度 (0-1)
    start_time: Optional[float]  # 开始时间戳
    end_time: Optional[float]  # 结束时间戳

def initialize_state() -> StreamState:
    """初始化状态"""
    return {
        "messages": [
            SystemMessage(content="你是一个有用的AI助手，擅长提供详尽的信息。")
        ],
        "current_response": None,
        "thinking": None,
        "progress": None,
        "start_time": None,
        "end_time": None
    }

# ===========================================================
# 第2部分: 配置LLM（修复版）
# ===========================================================

# 修复2: 改进异常处理
def create_llm():
    """创建LLM实例，带更好的错误处理"""
    try:
        llm = Ollama(model="llama3:latest", temperature=0.7)
        print("✅ 成功连接到Ollama模型")
        return llm
    except ConnectionError as e:
        print(f"❌ 连接错误: 无法连接到Ollama服务 - {e}")
        print("请确保Ollama服务正在运行: ollama serve")
    except Exception as e:
        print(f"❌ 其他错误: {e}")
    
    print("⚠️ 使用模拟LLM进行演示")
    return create_mock_llm()

def create_mock_llm():
    """创建模拟LLM（修复版）"""
    class MockLLM:
        def invoke(self, prompt, **kwargs):
            print(f"模拟LLM接收到提示: {prompt[:50]}...")
            return "这是模拟LLM的响应，用于演示流式输出功能。"
        
        # 修复3: 改进 stream 方法返回格式
        def stream(self, prompt, **kwargs):
            print(f"模拟LLM开始流式输出...")
            response = "这是模拟LLM的响应，用于演示流式输出功能。"
            for word in response.split():
                time.sleep(0.1)
                # 返回符合 LangChain 格式的数据
                yield {"content": word + " "}
    
    return MockLLM()

# 创建LLM实例
llm = create_llm()

# ===========================================================
# 第3部分: 节点函数定义
# ===========================================================

def start_generation(state: StreamState) -> StreamState:
    """开始生成流程，记录起始时间"""
    print("🕒 开始生成...")
    return {
        **state,
        "start_time": time.time(),
        "progress": 0.0
    }

def generate_thinking(state: StreamState) -> StreamState:
    """生成思考过程"""
    print("🧠 生成思考过程...")
    
    messages = state["messages"]
    if not any(isinstance(msg, HumanMessage) for msg in messages):
        return {**state, "thinking": "没有用户输入，无法生成思考过程"}
    
    last_user_msg = next((msg.content for msg in reversed(messages) 
                         if isinstance(msg, HumanMessage)), "")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "分析以下用户问题，思考如何回答（这个思考过程不会展示给用户）:"),
        ("user", "{input}")
    ])
    
    thinking_chain = prompt | llm | StrOutputParser()
    thinking = thinking_chain.invoke({"input": last_user_msg})
    
    return {
        **state,
        "thinking": thinking,
        "progress": 0.3
    }

def generate_response(state: StreamState) -> StreamState:
    """生成最终回复"""
    print("💬 生成回复...")
    
    messages = state["messages"]
    thinking = state.get("thinking", "")
    
    if not any(isinstance(msg, HumanMessage) for msg in messages):
        return {**state, "current_response": "你好！有什么我可以帮助你的吗？"}
    
    last_user_msg = next((msg.content for msg in reversed(messages) 
                         if isinstance(msg, HumanMessage)), "")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个有用的AI助手。使用以下思考过程来帮助回答，但不要在回复中提及这个思考过程:\n{thinking}"),
        ("user", "{input}")
    ])
    
    response_chain = prompt | llm | StrOutputParser()
    response = response_chain.invoke({
        "thinking": thinking,
        "input": last_user_msg
    })
    
    new_messages = messages.copy()
    new_messages.append(AIMessage(content=response))
    
    return {
        **state,
        "messages": new_messages,
        "current_response": response,
        "progress": 1.0,
        "end_time": time.time()
    }

# 修复4: 改进进度更新逻辑
def update_progress(state: StreamState) -> StreamState:
    """更新进度信息（改进版）"""
    current_progress = state.get("progress", 0)
    start_time = state.get("start_time", time.time())
    
    # 基于时间计算进度，更真实
    if current_progress < 1.0:
        elapsed_time = time.time() - start_time
        # 假设总生成时间约为3秒
        estimated_total_time = 3.0
        time_based_progress = min(elapsed_time / estimated_total_time, 0.9)
        
        # 取当前进度和时间进度的较大值
        new_progress = max(current_progress + 0.05, time_based_progress)
        new_progress = min(new_progress, 0.9)  # 最多到90%
        
        print(f"📊 进度更新: {new_progress:.1f}")
        
        return {
            **state,
            "progress": new_progress
        }
    
    return state

# ===========================================================
# 第4部分: 创建图结构
# ===========================================================

def create_basic_graph():
    """创建基本流式处理图"""
    workflow = StateGraph(StreamState)
    
    workflow.add_node("start", start_generation)
    workflow.add_node("thinking", generate_thinking)
    workflow.add_node("respond", generate_response)
    
    workflow.add_edge("start", "thinking")
    workflow.add_edge("thinking", "respond")
    workflow.add_edge("respond", END)
    
    workflow.set_entry_point("start")
    
    return workflow.compile()

def create_advanced_stream_graph():
    """创建高级流式处理图"""
    workflow = StateGraph(StreamState)
    
    workflow.add_node("start", start_generation)
    workflow.add_node("thinking", generate_thinking)
    workflow.add_node("update_progress", update_progress)
    workflow.add_node("respond", generate_response)
    
    workflow.add_edge("start", "thinking")
    workflow.add_edge("thinking", "update_progress")
    workflow.add_edge("update_progress", "respond")
    workflow.add_edge("respond", END)
    
    workflow.set_entry_point("start")
    
    return workflow.compile()

# ===========================================================
# 第5部分: 流式输出示例
# ===========================================================

def run_basic_stream_example():
    """运行基本流式处理示例"""
    print("\n===== 基本流式处理示例 =====")
    
    graph = create_basic_graph()
    
    state = initialize_state()
    state["messages"].append(HumanMessage(content="介绍一下中国的四大发明"))
    
    config = {"recursion_limit": 25}
    
    print("\n开始流式处理...")
    events = graph.stream(
        state,
        config,
        stream_mode="values"
    )
    
    for i, event in enumerate(events):
        print(f"\n事件 #{i+1}:")
        
        if "progress" in event:
            print(f"进度: {event['progress']:.1%}")
        
        if "thinking" in event and event["thinking"]:
            print(f"思考: {event['thinking'][:50]}..." if event["thinking"] else "")
        
        if "current_response" in event and event["current_response"]:
            print(f"响应: {event['current_response'][:50]}..." if event["current_response"] else "")
        
        if "end_time" in event and event["end_time"]:
            start = event.get("start_time", 0)
            end = event["end_time"]
            if start and end:
                print(f"生成耗时: {end - start:.2f}秒")

def run_advanced_stream_example():
    """运行高级流式处理示例"""
    print("\n===== 高级流式处理示例 =====")
    
    graph = create_advanced_stream_graph()
    
    state = initialize_state()
    state["messages"].append(HumanMessage(content="解释量子物理的基本原理"))
    
    config = {"recursion_limit": 25}
    
    print("\n开始流式处理，带格式化输出...")
    
    events = graph.stream(
        state,
        config,
        stream_mode="updates"
    )
    
    for event in events:
        event_type = event.get("event")
        if event_type == "on_chain_start":
            node_name = event.get("name", "unknown")
            print(f"\n🔄 开始执行节点: {node_name}")
            
        elif event_type == "on_chain_end":
            node_name = event.get("name", "unknown")
            print(f"✅ 完成节点: {node_name}")
            
            if "output" in event:
                output = event["output"]
                if isinstance(output, dict):
                    if "progress" in output:
                        print(f"📈 当前进度: {output['progress']:.1%}")
                    if "thinking" in output and output["thinking"]:
                        print(f"🧠 思考: {output['thinking'][:100]}..." if len(output['thinking']) > 100 else output['thinking'])
                    if "current_response" in output and output["current_response"]:
                        print(f"💬 响应: {output['current_response']}")
                        
        elif event_type == "on_chain_error":
            error = event.get("error", "未知错误")
            print(f"❌ 错误: {error}")

# ===========================================================
# 第6部分: 字符级流式输出
# ===========================================================

def create_character_stream_chain():
    """创建字符级流式输出处理链"""
    chain = (
        RunnablePassthrough() 
        | {
            "messages": lambda x: x["messages"],
            "prompt": lambda x: format_prompt_from_messages(x["messages"])
        }
    )
    return chain

# 修复5: 改进 token 估算方法
def estimate_tokens(text: str) -> int:
    """更准确的 token 估算（改进版）"""
    if not text:
        return 0
    
    # 中文字符和英文单词的混合估算
    chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    english_words = len([word for word in text.split() if word.isascii()])
    
    # 中文字符通常1个字符≈1个token，英文单词≈1.3个token
    estimated_tokens = chinese_chars + int(english_words * 1.3)
    
    return max(estimated_tokens, 1)  # 至少1个token

def format_prompt_from_messages(messages: List[BaseMessage]) -> str:
    """从消息列表格式化提示字符串（修复版）"""
    formatted_prompt = ""
    for message in messages:
        if isinstance(message, SystemMessage):
            formatted_prompt += f"系统: {message.content}\n\n"
        elif isinstance(message, HumanMessage):
            formatted_prompt += f"用户: {message.content}\n\n"
        elif isinstance(message, AIMessage):
            formatted_prompt += f"AI: {message.content}\n\n"
    
    formatted_prompt += "AI: "
    return formatted_prompt

def run_character_stream_example():
    """运行字符级流式输出示例"""
    print("\n===== 字符级流式输出示例 =====")
    
    state = initialize_state()
    state["messages"].append(HumanMessage(content="写一首关于春天的短诗"))
    
    chain = create_character_stream_chain()
    processed_input = chain.invoke(state)
    prompt = processed_input["prompt"]
    
    print("\n开始字符级流式输出...")
    print("用户: 写一首关于春天的短诗")
    print("AI: ", end="", flush=True)
    
    response_tokens = []
    try:
        for token in llm.stream(prompt):
            if isinstance(token, dict) and "content" in token:
                content = token["content"]
            else:
                content = str(token)
            
            print(content, end="", flush=True)
            response_tokens.append(content)
            time.sleep(0.05)
    except Exception as e:
        print(f"\n流式输出错误: {e}")
        return
    
    full_response = "".join(response_tokens)
    
    state["messages"].append(AIMessage(content=full_response))
    state["current_response"] = full_response
    state["progress"] = 1.0
    state["end_time"] = time.time()
    
    print("\n\n✅ 字符级流式输出完成")

# ===========================================================
# 第7部分: 回调处理器（修复版）
# ===========================================================

class CustomCallbackHandler(BaseCallbackHandler):
    """自定义回调处理器（修复版）"""
    
    def __init__(self):
        super().__init__()
        self.steps = 0
        self.node_times = {}
        self.node_start_times = {}
        self.total_tokens = 0
    
    def on_chain_start(self, serialized: dict, inputs: dict, **kwargs):
        """当链/节点开始执行时调用"""
        node_name = serialized.get("name", "unknown")
        self.node_start_times[node_name] = time.time()
        print(f">> 开始执行: {node_name}")
    
    def on_chain_end(self, outputs: dict, **kwargs):
        """当链/节点执行完成时调用（修复版）"""
        self.steps += 1
        
        serialized = kwargs.get("serialized", {})
        node_name = serialized.get("name", "unknown")
        
        if node_name in self.node_start_times:
            start_time = self.node_start_times[node_name]
            end_time = time.time()
            execution_time = end_time - start_time
            
            if node_name in self.node_times:
                self.node_times[node_name] += execution_time
            else:
                self.node_times[node_name] = execution_time
            
            print(f"<< 完成执行: {node_name} (耗时: {execution_time:.2f}秒)")
            
            # 修复5: 使用改进的 token 估算
            if isinstance(outputs, dict):
                if "thinking" in outputs and outputs["thinking"]:
                    tokens = estimate_tokens(outputs["thinking"])
                    self.total_tokens += tokens
                if "current_response" in outputs and outputs["current_response"]:
                    tokens = estimate_tokens(outputs["current_response"])
                    self.total_tokens += tokens
    
    def on_chain_error(self, error: Exception, **kwargs):
        """当链/节点执行出错时调用"""
        serialized = kwargs.get("serialized", {})
        node_name = serialized.get("name", "unknown")
        print(f"!! 错误: {node_name} - {str(error)}")
    
    def get_summary(self):
        """获取执行摘要"""
        return {
            "steps": self.steps,
            "node_times": self.node_times,
            "total_tokens": self.total_tokens
        }

def run_callback_example():
    """运行带回调的流式处理示例"""
    print("\n===== 事件监听与回调示例 =====")
    
    graph = create_basic_graph()
    
    state = initialize_state()
    state["messages"].append(HumanMessage(content="介绍人工智能的历史和未来发展趋势"))
    
    callback_handler = CustomCallbackHandler()
    
    config = {
        "recursion_limit": 25,
        "callbacks": [callback_handler]
    }
    
    print("\n开始执行流程，带事件监听...")
    
    try:
        result = graph.invoke(state, config)
        
        print("\n===== 执行摘要 =====")
        summary = callback_handler.get_summary()
        print(f"执行步骤: {summary['steps']}")
        print(f"总token数: {summary['total_tokens']}")
        print("节点执行时间:")
        for node, time_taken in summary['node_times'].items():
            print(f"  - {node}: {time_taken:.2f}秒")
        
        if result and "messages" in result and result["messages"]:
            print("\n最终回复:")
            print(result["messages"][-1].content)
            
    except Exception as e:
        print(f"执行过程中发生错误: {e}")

# ===========================================================
# 第8部分: 主函数
# ===========================================================

if __name__ == "__main__":
    print("===== LangGraph 流式处理与实时反馈示例（修复版）=====\n")
    
    try:
        # # 1. 运行基本流式处理示例
        # run_basic_stream_example()
        # input("\n按Enter继续下一个示例...")
        
        # 2. 运行高级流式处理示例
        run_advanced_stream_example()
        input("\n按Enter继续下一个示例...")
        
        # 3. 运行字符级流式输出示例
        run_character_stream_example()
        input("\n按Enter继续下一个示例...")
        
        # 4. 运行事件监听与回调示例
        run_callback_example()
        
        print("\n===== 所有示例执行完毕 =====")
        print("修复的问题:")
        print("✅ 添加了缺失的 BaseMessage 导入")
        print("✅ 改进了异常处理")
        print("✅ 修复了 MockLLM 的 stream 方法")
        print("✅ 改进了进度更新逻辑")
        print("✅ 优化了 token 估算方法")
        
    except KeyboardInterrupt:
        print("\n\n用户中断执行")
    except Exception as e:
        print(f"\n执行过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
