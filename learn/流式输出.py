#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""流式输出 - LangGraph流式处理与实时反馈示例

WHY - 设计思路:
1. 在AI系统中，实时反馈对用户体验至关重要，而不是让用户等待完整结果
2. 传统的异步模式下，用户需要等待整个处理完成才能获得结果
3. 流式输出可以展示思考过程、进度更新和逐步生成，增强交互性
4. 对于复杂任务，用户需要了解处理进度以减少等待焦虑

HOW - 实现方式:
1. 使用LangGraph的stream API代替标准invoke
2. 设计包含状态跟踪字段的状态结构(StreamState)
3. 实现不同粒度的流式处理:
   - 状态级流式输出: 每次状态更新时返回完整状态
   - 事件级流式输出: 每次节点执行时返回事件通知
   - 字符级流式输出: 直接从LLM获取逐个令牌
4. 使用回调系统获取更详细的执行指标和性能数据

WHAT - 功能作用:
本示例演示了LangGraph中的多种流式处理模式，提供四个主要示例:
1. 基本流式处理: 展示如何获取状态更新流
2. 高级流式处理: 展示如何处理事件流和详细元数据
3. 字符级流式输出: 展示如何实现更细粒度的输出
4. 回调与监控: 展示如何跟踪图执行过程的详细信息

这些示例涵盖了从简单到复杂的流式处理场景，适用于构建具有良好用户体验的AI应用。
"""

from typing import TypedDict, List, Dict, Any, Optional, Union, Literal
import time
import json
from datetime import datetime

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
    """流式处理状态定义
    
    WHY - 设计思路:
    1. 在流式处理中，我们需要追踪不仅是最终结果，还包括中间生成过程
    2. 为了支持实时进度显示，需要记录完成百分比
    3. 用户体验要求我们能够测量和展示响应生成的时间
    4. 流式处理需要区分内部思考过程和向用户展示的最终回复
    
    HOW - 实现方式:
    通过TypedDict定义带类型提示的状态结构，包含:
    - 标准的消息历史记录字段
    - 专门的当前响应字段，可实时更新
    - 思考过程字段，存储LLM的内部推理但不直接展示给用户
    - 进度跟踪字段，用于UI进度条
    - 时间戳字段，用于性能测量
    
    WHAT - 功能作用:
    提供一个完整的状态容器，承载流式生成过程中的各类数据，
    使得整个生成过程变得可观察、可测量且对用户友好
    """
    messages: List[Union[HumanMessage, AIMessage, SystemMessage]]  # 消息历史
    current_response: Optional[str]  # 当前正在生成的响应
    thinking: Optional[str]  # 思考过程
    progress: Optional[float]  # 生成进度 (0-1)
    start_time: Optional[float]  # 开始时间戳
    end_time: Optional[float]  # 结束时间戳

def initialize_state() -> StreamState:
    """初始化状态
    
    WHY - 设计思路:
    1. 每次流式生成需要一个干净的初始状态
    2. 系统提示信息需要预设，定义AI助手的行为方式
    3. 所有追踪字段需要初始化为空值或默认值
    
    HOW - 实现方式:
    创建一个包含所有必要字段的StreamState字典:
    - 初始化消息列表，包含系统指令
    - 将其他所有追踪字段设为None
    
    WHAT - 功能作用:
    提供一个一致的起点，确保每次流式处理开始时状态干净且可预测，
    避免上一次生成的残留数据影响新的生成过程
    """
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
# 第2部分: 配置LLM
# ===========================================================

# 尝试使用Ollama本地模型，如果不可用，打印提示信息
try:
    llm = Ollama(model="llama3:latest", temperature=0.7)
    print("成功连接到Ollama模型")
except:
    print("警告: 无法连接到Ollama模型，请确保Ollama服务正在运行")
    print("你可以通过以下命令启动Ollama并拉取模型:")
    print("  1. 启动Ollama服务")
    print("  2. 执行: ollama pull llama3")
    
    # 创建一个模拟LLM用于演示
    class MockLLM:
        def invoke(self, prompt, **kwargs):
            print(f"模拟LLM接收到提示: {prompt[:50]}...")
            return "这是模拟LLM的响应，用于演示流式输出功能。实际使用时，这里会是真实模型的输出。"
        
        def stream(self, prompt, **kwargs):
            print(f"模拟LLM开始流式输出...")
            response = "这是模拟LLM的响应，用于演示流式输出功能。实际使用时，这里会是真实模型的输出。"
            for word in response.split():
                time.sleep(0.1)  # 模拟生成延迟
                yield word + " "
    
    llm = MockLLM()

# ===========================================================
# 第3部分: 节点函数定义
# ===========================================================

def start_generation(state: StreamState) -> StreamState:
    """开始生成流程，记录起始时间
    
    WHY - 设计思路:
    1. 流式生成需要一个明确的起点，用于后续计时和进度跟踪
    2. 用户需要知道生成过程已经开始
    3. 为了准确计算总生成时间，需要记录精确的开始时间戳
    
    HOW - 实现方式:
    接收当前状态，然后:
    - 记录当前时间作为开始时间戳
    - 初始化进度为0.0，表示刚刚开始
    - 保持状态的其他部分不变
    
    WHAT - 功能作用:
    标记生成过程的开始点，初始化进度跟踪，为后续的进度更新和
    性能测量提供基准点
    """
    print("🕒 开始生成...")
    return {
        **state,
        "start_time": time.time(),
        "progress": 0.0
    }

def generate_thinking(state: StreamState) -> StreamState:
    """生成思考过程（不直接可见给用户）
    
    WHY - 设计思路:
    1. 高质量回复需要先进行深入思考，然后再组织回复
    2. 内部思考过程对调试和分析非常有价值，但不应直接展示给用户
    3. 让AI先思考可以提高最终回复的质量和相关性
    4. 思考过程可以用于显示部分进度，提高用户等待体验
    
    HOW - 实现方式:
    1. 检查状态中是否有用户消息
    2. 提取最后一条用户消息内容
    3. 使用专门提示让LLM生成思考过程
    4. 通过链式调用生成思考内容
    5. 更新状态的思考字段和进度
    
    WHAT - 功能作用:
    生成LLM内部的分析和推理过程，为最终回复提供基础，
    同时更新进度到约30%，表明生成工作正在进行
    """
    print("🧠 生成思考过程...")
    
    # 获取消息历史
    messages = state["messages"]
    if not any(isinstance(msg, HumanMessage) for msg in messages):
        return {**state, "thinking": "没有用户输入，无法生成思考过程"}
    
    # 获取最后一条用户消息
    last_user_msg = next((msg.content for msg in reversed(messages) 
                         if isinstance(msg, HumanMessage)), "")
    
    # 使用LLM生成思考过程
    prompt = ChatPromptTemplate.from_messages([
        ("system", "分析以下用户问题，思考如何回答（这个思考过程不会展示给用户）:"),
        ("user", "{input}")
    ])
    
    thinking_chain = prompt | llm | StrOutputParser()
    thinking = thinking_chain.invoke({"input": last_user_msg})
    
    # 更新进度
    return {
        **state,
        "thinking": thinking,
        "progress": 0.3  # 思考过程占总进度的30%
    }

def generate_response(state: StreamState) -> StreamState:
    """生成最终回复
    
    WHY - 设计思路:
    1. 有了思考过程后，需要生成一个精炼的、面向用户的回复
    2. 回复应该利用思考过程的洞见，但不直接暴露思考细节
    3. 回复需要保存到消息历史中，以支持多轮对话
    4. 生成完成后需要标记整个流程已结束
    
    HOW - 实现方式:
    1. 从状态中获取消息历史和思考过程
    2. 使用特殊提示，指导LLM基于思考过程生成回复
    3. 创建响应链并调用LLM生成回复
    4. 将回复添加到消息历史
    5. 更新状态，标记进度为100%并记录结束时间
    
    WHAT - 功能作用:
    利用前面生成的思考内容，创建一个高质量的用户可见回复，
    更新对话历史，并标记生成过程完成
    """
    print("💬 生成回复...")
    
    # 获取消息历史和思考过程
    messages = state["messages"]
    thinking = state.get("thinking", "")
    
    if not any(isinstance(msg, HumanMessage) for msg in messages):
        return {**state, "current_response": "你好！有什么我可以帮助你的吗？"}
    
    # 获取最后一条用户消息
    last_user_msg = next((msg.content for msg in reversed(messages) 
                         if isinstance(msg, HumanMessage)), "")
    
    # 使用带思考过程的提示来生成回复
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个有用的AI助手。使用以下思考过程来帮助回答，但不要在回复中提及这个思考过程:\n{thinking}"),
        ("user", "{input}")
    ])
    
    response_chain = prompt | llm | StrOutputParser()
    response = response_chain.invoke({
        "thinking": thinking,
        "input": last_user_msg
    })
    
    # 更新状态
    new_messages = messages.copy()
    new_messages.append(AIMessage(content=response))
    
    return {
        **state,
        "messages": new_messages,
        "current_response": response,
        "progress": 1.0,  # 完成生成
        "end_time": time.time()
    }

def update_progress(state: StreamState) -> StreamState:
    """更新进度信息
    
    WHY - 设计思路:
    1. 即使没有实质性进展，用户也需要看到进度变化，以确认系统仍在工作
    2. 渐进式更新进度可以提高用户等待体验，减少焦虑感
    3. 给用户提供精细的进度反馈比简单的"正在处理"更有价值
    
    HOW - 实现方式:
    1. 获取当前进度值
    2. 如果未达到完成状态，则增加一个小的进度量
    3. 限制最大进度到90%，预留10%给最终完成步骤
    4. 返回带有更新进度的状态
    
    WHAT - 功能作用:
    模拟细粒度的进度更新，在实际计算进行期间给用户提供视觉反馈，
    使长时间运行的操作显得更加平滑和可预测
    """
    current_progress = state.get("progress", 0)
    
    # 模拟进度更新
    if current_progress < 1.0:
        new_progress = min(current_progress + 0.1, 0.9)  # 最多更新到90%，留10%给最终完成
        print(f"📊 进度更新: {new_progress:.1f}")
        
        return {
            **state,
            "progress": new_progress
        }
    
    return state

# ===========================================================
# 第4部分: 创建基本图结构
# ===========================================================

def create_basic_graph():
    """创建基本流式处理图
    
    WHY - 设计思路:
    1. 需要一个简单且可重用的流式处理工作流结构
    2. 流程需要包含生成的各个关键阶段（开始、思考、回复）
    3. 节点和边需要有明确的组织，便于理解和修改
    
    HOW - 实现方式:
    1. 创建一个使用StreamState类型的图
    2. 添加三个主要节点，代表生成过程的三个阶段
    3. 定义节点间的线性流动路径
    4. 设置workflow的入口点
    5. 返回编译后的图，使其可执行
    
    WHAT - 功能作用:
    提供一个基础的线性流式处理图结构，实现从开始到思考再到回复的
    基本流程，为流式输出功能提供骨架
    """
    # 创建图实例
    workflow = StateGraph(StreamState)
    
    # 添加节点
    workflow.add_node("start", start_generation)
    workflow.add_node("thinking", generate_thinking)
    workflow.add_node("respond", generate_response)
    
    # 添加边
    workflow.add_edge("start", "thinking")
    workflow.add_edge("thinking", "respond")
    workflow.add_edge("respond", END)
    
    # 设置入口点
    workflow.set_entry_point("start")
    
    # 编译图
    return workflow.compile()

# ===========================================================
# 第5部分: 流式输出与事件处理
# ===========================================================

def run_basic_stream_example():
    """运行基本流式处理示例
    
    WHY - 设计思路:
    1. 需要展示流式处理的基本工作方式和API使用
    2. 用户需要一个简单的示例来理解流式输出和普通输出的区别
    3. 实例应该展示如何获取和使用流式状态更新
    
    HOW - 实现方式:
    1. 创建基本流程图
    2. 准备初始状态，包含一个示例用户查询
    3. 使用stream方法代替invoke，指定stream_mode为"values"
    4. 迭代事件流，提取并展示关键状态字段
    5. 展示生成过程中的进度、思考和最终响应
    
    WHAT - 功能作用:
    提供一个完整的流式处理演示，展示LangGraph中stream API的使用方法，
    并呈现流式处理过程中的各个状态更新
    """
    print("\n===== 基本流式处理示例 =====")
    
    # 创建图
    graph = create_basic_graph()
    
    # 初始化状态
    state = initialize_state()
    state["messages"].append(HumanMessage(content="介绍一下中国的四大发明"))
    
    # 配置
    config = {"recursion_limit": 25}
    
    print("\n开始流式处理...")
    # 使用stream方法，而不是invoke
    events = graph.stream(
        state,
        config,
        stream_mode="values"  # 流式返回状态值
    )
    
    # 处理事件流
    for i, event in enumerate(events):
        print(f"\n事件 #{i+1}:")
        
        if "progress" in event and event["progress"] is not None:
            print(f"进度: {event['progress']:.1%}")
        elif "progress" in event:
            print(f"进度: {event['progress']}")
        
        if "thinking" in event and event["thinking"]:
            print(f"思考: {event['thinking'][:50]}..." if event["thinking"] else "")
        
        if "current_response" in event and event["current_response"]:
            print(f"响应: {event['current_response'][:50]}..." if event["current_response"] else "")
        
        if "end_time" in event and event["end_time"]:
            start = event.get("start_time", 0)
            end = event["end_time"]
            if start and end:
                print(f"生成耗时: {end - start:.2f}秒")

# ===========================================================
# 第6部分: 高级流式处理与格式化
# ===========================================================

def create_advanced_stream_graph():
    """创建高级流式处理图，包含进度更新节点
    
    WHY - 设计思路:
    1. 基本图缺乏中间进度更新，让用户体验不够平滑
    2. 在思考和回复之间需要更细粒度的进度反馈
    3. 进度更新可以减少用户的等待焦虑
    
    HOW - 实现方式:
    1. 创建一个使用StreamState类型的图
    2. 除了基本节点外，额外添加进度更新节点
    3. 调整边，使流程经过进度更新节点
    4. 设置workflow的入口点
    5. 返回编译后的图，使其可执行
    
    WHAT - 功能作用:
    提供一个增强版的流式处理图，添加了额外的进度更新环节，
    优化了用户等待体验，使进度展示更平滑
    """
    # 创建图实例
    workflow = StateGraph(StreamState)
    
    # 添加节点
    workflow.add_node("start", start_generation)
    workflow.add_node("thinking", generate_thinking)
    workflow.add_node("update_progress", update_progress)  # 添加进度更新节点
    workflow.add_node("respond", generate_response)
    
    # 添加边
    workflow.add_edge("start", "thinking")
    workflow.add_edge("thinking", "update_progress")
    workflow.add_edge("update_progress", "respond")
    workflow.add_edge("respond", END)
    
    # 设置入口点
    workflow.set_entry_point("start")
    
    # 编译图
    return workflow.compile()

def run_advanced_stream_example():
    """运行高级流式处理示例
    
    WHY - 设计思路:
    1. 需要展示更复杂的流式处理模式和更精细的事件监听
    2. 基本示例只展示了状态值，但事件类型和元数据同样重要
    3. 用户需要了解如何处理不同类型的事件和状态更新
    
    HOW - 实现方式:
    1. 创建高级流程图（包含进度更新节点）
    2. 准备初始状态，包含一个示例用户查询
    3. 使用回调处理器监听详细事件
    4. 结合流式状态更新和事件监听
    5. 对事件内容进行格式化，提高可读性
    
    WHAT - 功能作用:
    提供一个更高级的流式处理演示，专注于事件类型和事件处理模式，
    展示如何监听节点执行过程并提取详细信息
    """
    print("\n===== 高级流式处理示例 =====")
    
    # 创建图
    graph = create_advanced_stream_graph()
    
    # 初始化状态
    state = initialize_state()
    state["messages"].append(HumanMessage(content="解释量子物理的基本原理"))
    
    # 创建回调处理器
    callback_handler = create_callback_handlers()
    
    # 配置
    config = {
        "recursion_limit": 25,
        "callbacks": [callback_handler]  # 添加回调处理器
    }
    
    print("\n开始流式处理，带事件监听...")
    
    # 流式处理 - 使用 "values" 模式获取状态更新
    events = graph.stream(
        state,
        config,
        stream_mode="values"  # 流式返回状态值
    )
    
    # 格式化事件输出
    for i, event in enumerate(events):
        print(f"\n事件 #{i+1}:")
        
        # 检查进度更新
        if "progress" in event and event["progress"] is not None:
            print(f"📈 进度: {event['progress']:.1%}")
        elif "progress" in event:
            print(f"📈 进度: {event['progress']}")
        
        # 检查思考过程
        if "thinking" in event and event["thinking"]:
            print(f"🧠 思考: {event['thinking'][:100]}..." if len(event['thinking']) > 100 else event['thinking'])
        
        # 检查响应更新
        if "current_response" in event and event["current_response"]:
            print(f"💬 响应: {event['current_response']}")
        
        # 检查时间信息
        if "end_time" in event and event["end_time"]:
            start = event.get("start_time", 0)
            end = event["end_time"]
            if start and end:
                print(f"⏱️ 生成耗时: {end - start:.2f}秒")
    
    # 打印回调摘要
    print("\n===== 事件监听摘要 =====")
    summary = callback_handler.get_summary()
    print(f"执行步骤: {summary['steps']}")
    print(f"总token数: {summary['total_tokens']}")
    print("节点执行时间:")
    for node, time_taken in summary['node_times'].items():
        print(f"  - {node}: {time_taken:.2f}秒")

# ===========================================================
# 第7部分: 字符级流式输出
# ===========================================================

def create_character_stream_chain():
    """创建字符级流式输出处理链
    
    WHY - 设计思路:
    1. 纯图级流式处理通常返回整个对象或状态，无法提供字符级细粒度
    2. 需要一个独立于图的机制直接从LLM获取流式令牌
    3. 需要一个简单的处理流程将状态转换为适合LLM的提示格式
    
    HOW - 实现方式:
    1. 使用RunnablePassthrough保留输入状态
    2. 使用映射函数从输入状态提取消息历史
    3. 使用格式化函数创建完整的提示模板
    4. 将这些步骤链接成一个处理管道
    
    WHAT - 功能作用:
    返回一个用于字符流处理的轻量级处理链，该链将状态对象转换为
    LLM可以直接处理的提示格式，便于使用LLM的stream方法
    """
    # 创建一个链，处理输入并准备提示
    chain = (
        RunnablePassthrough() 
        | {
            "messages": lambda x: x["messages"],
            "prompt": lambda x: format_prompt_from_messages(x["messages"])
        }
    )
    return chain

def run_character_stream_example():
    """运行字符级流式输出示例
    
    WHY - 设计思路:
    1. 图级流式处理粒度较粗，无法实现逐字符的平滑输出效果
    2. 用户期望类似ChatGPT那样的逐字符输出，体验更佳
    3. 需要展示如何直接使用LLM的stream方法实现细粒度输出
    
    HOW - 实现方式:
    1. 创建一个处理链，将状态转换为适合LLM的提示格式
    2. 准备初始状态，包含一个示例用户查询
    3. 直接使用LLM的stream方法获取令牌流
    4. 实时打印每个令牌，模拟逐字输出效果
    5. 收集完整响应并更新最终状态
    
    WHAT - 功能作用:
    提供一个字符级流式输出的演示，展示如何实现更细粒度、更流畅的
    输出效果，提高用户交互体验
    """
    print("\n===== 字符级流式输出示例 =====")
    
    # 初始化状态
    state = initialize_state()
    state["messages"].append(HumanMessage(content="写一首关于春天的短诗"))
    
    # 创建链
    chain = create_character_stream_chain()
    
    # 转换状态
    processed_input = chain.invoke(state)
    prompt = processed_input["prompt"]
    
    print("\n开始字符级流式输出...")
    print("用户: 写一首关于春天的短诗")
    print("AI: ", end="", flush=True)
    
    # 流式输出
    response_tokens = []
    for token in llm.stream(prompt):
        # 模拟逐字符输出
        print(token, end="", flush=True)
        response_tokens.append(token)
        time.sleep(0.05)  # 添加延迟使输出更清晰可见
    
    # 收集完整响应
    full_response = "".join(response_tokens)
    
    # 更新状态
    state["messages"].append(AIMessage(content=full_response))
    state["current_response"] = full_response
    state["progress"] = 1.0
    state["end_time"] = time.time()
    
    print("\n\n✅ 字符级流式输出完成")

# ===========================================================
# 第8部分: 事件监听与回调
# ===========================================================

class CustomCallbackHandler(BaseCallbackHandler):
    """自定义回调处理器
    
    WHY - 设计思路:
    1. 需要一种机制来监控图执行的详细过程，超出流式状态更新之外
    2. 需要收集性能指标和执行统计信息，如耗时和token使用量
    3. 回调系统提供了更灵活的集成点，可以连接到外部监控或日志系统
    
    HOW - 实现方式:
    1. 继承BaseCallbackHandler基类，实现核心回调方法
    2. 维护内部状态来跟踪执行过程的关键指标
    3. 提供方法收集和汇总执行信息
    4. 在关键事件（开始、结束、错误）时捕获相关数据
    
    WHAT - 功能作用:
    提供一个可插拔的监控组件，用于跟踪图执行过程中的各种事件，
    收集节点执行时间、token使用情况和步骤顺序等关键指标
    """
    def __init__(self):
        """初始化回调处理器
        
        初始化各种计数器和跟踪变量，为监控图执行做准备
        """
        super().__init__()
        # 跟踪执行步骤
        self.steps = 0
        # 记录节点执行时间
        self.node_times = {}
        # 记录节点开始时间
        self.node_start_times = {}
        # 记录总token使用量
        self.total_tokens = 0
    
    def on_chain_start(self, serialized: dict, inputs: dict, **kwargs):
        """当链/节点开始执行时调用
        
        WHY: 需要记录节点执行的开始时间，为计算耗时做准备
        HOW: 获取节点名称，记录当前时间戳
        WHAT: 跟踪节点执行的起始点
        """
        # 修复：处理 serialized 可能为 None 的情况
        if serialized is None:
            serialized = {}
        node_name = serialized.get("name", "unknown")
        self.node_start_times[node_name] = time.time()
        print(f">> 开始执行: {node_name}")
    
    def on_chain_end(self, outputs: dict, **kwargs):
        """当链/节点执行完成时调用
        
        WHY: 需要计算节点执行时间，记录输出信息，并更新统计数据
        HOW: 获取节点名称，计算耗时，分析输出，更新计数器
        WHAT: 跟踪节点执行的完成情况及其输出
        """
        self.steps += 1
        
        # 从kwargs中获取序列化信息
        serialized = kwargs.get("serialized", {})
        node_name = serialized.get("name", "unknown")
        
        # 计算执行时间
        if node_name in self.node_start_times:
            start_time = self.node_start_times[node_name]
            end_time = time.time()
            execution_time = end_time - start_time
            
            # 累加节点执行时间
            if node_name in self.node_times:
                self.node_times[node_name] += execution_time
            else:
                self.node_times[node_name] = execution_time
            
            print(f"<< 完成执行: {node_name} (耗时: {execution_time:.2f}秒)")
            
            # 估算token使用量（简化版）
            if isinstance(outputs, dict) and "thinking" in outputs and outputs["thinking"]:
                # 非常粗略的估计，仅用于演示
                tokens = len(outputs["thinking"]) // 4
                self.total_tokens += tokens
    
    def on_chain_error(self, error: Exception, **kwargs):
        """当链/节点执行出错时调用
        
        WHY: 需要捕获和记录错误信息，便于调试和错误处理
        HOW: 获取节点名称和错误详情，格式化输出
        WHAT: 提供错误跟踪和诊断信息
        """
        # 从kwargs中获取序列化信息
        serialized = kwargs.get("serialized", {})
        node_name = serialized.get("name", "unknown")
        
        print(f"!! 错误: {node_name} - {str(error)}")
    
    def get_summary(self):
        """获取执行摘要
        
        WHY: 需要一种方式汇总和呈现所收集的所有执行指标
        HOW: 整合各类统计数据，构建摘要字典
        WHAT: 提供完整的执行性能和行为概览
        """
        return {
            "steps": self.steps,
            "node_times": self.node_times,
            "total_tokens": self.total_tokens
        }

def create_callback_handlers():
    """创建回调处理器实例
    
    WHY - 设计思路:
    1. 需要封装回调处理器的创建逻辑，便于复用
    2. 可能需要在创建时进行配置或自定义
    3. 将创建与使用分离，符合单一职责原则
    
    HOW - 实现方式:
    创建并返回一个配置好的CustomCallbackHandler实例
    
    WHAT - 功能作用:
    提供一个工厂函数，用于创建准备就绪的回调处理器
    """
    return CustomCallbackHandler()

def format_prompt_from_messages(messages: List[BaseMessage]) -> str:
    """从消息列表格式化提示字符串
    
    WHY - 设计思路:
    1. LLM的stream方法直接接受字符串提示，而不是消息列表
    2. 需要将结构化消息转换为适合LLM处理的文本格式
    3. 格式需要保持一致，确保LLM理解消息的角色和内容
    
    HOW - 实现方式:
    1. 遍历消息列表
    2. 根据消息类型添加对应的前缀（如"系统："、"用户："、"AI："）
    3. 拼接所有格式化的消息
    
    WHAT - 功能作用:
    将LangChain格式的消息列表转换为LLM可直接处理的文本提示，
    保留消息的角色信息
    """
    formatted_prompt = ""
    for message in messages:
        if isinstance(message, SystemMessage):
            formatted_prompt += f"系统: {message.content}\n\n"
        elif isinstance(message, HumanMessage):
            formatted_prompt += f"用户: {message.content}\n\n"
        elif isinstance(message, AIMessage):
            formatted_prompt += f"AI: {message.content}\n\n"
    
    # 添加最后的AI前缀，引导模型开始回复
    formatted_prompt += "AI: "
    return formatted_prompt

def run_callback_example():
    """运行带回调的流式处理示例
    
    WHY - 设计思路:
    1. 实际应用中常需要跟踪执行过程的详细信息和统计数据
    2. 用户需要了解回调系统如何工作以及如何收集自定义指标
    3. 回调可以用于性能分析、监控和调试
    
    HOW - 实现方式:
    1. 创建自定义回调处理器，实现关键回调方法
    2. 准备图和初始状态
    3. 在配置中添加回调处理器
    4. 使用普通invoke方法执行图（回调仍然有效）
    5. 从回调处理器收集执行摘要并显示
    
    WHAT - 功能作用:
    演示如何使用回调系统监控和分析LangGraph执行过程，
    收集执行步骤、耗时、token使用等关键指标
    """
    print("\n===== 事件监听与回调示例 =====")
    
    # 创建图
    graph = create_basic_graph()
    
    # 初始化状态
    state = initialize_state()
    state["messages"].append(HumanMessage(content="介绍人工智能的历史和未来发展趋势"))
    
    # 创建回调处理器
    callback_handler = create_callback_handlers()
    
    # 配置
    config = {
        "recursion_limit": 25,
        "callbacks": [callback_handler]  # 添加回调处理器
    }
    
    print("\n开始执行流程，带事件监听...")
    
    # 执行图
    result = graph.invoke(state, config)
    
    # 打印摘要
    print("\n===== 执行摘要 =====")
    summary = callback_handler.get_summary()
    print(f"执行步骤: {summary['steps']}")
    print(f"总token数: {summary['total_tokens']}")
    print("节点执行时间:")
    for node, time_taken in summary['node_times'].items():
        print(f"  - {node}: {time_taken:.2f}秒")
    
    # 返回响应
    if result and "messages" in result and result["messages"]:
        print("\n最终回复:")
        print(result["messages"][-1].content)

# ===========================================================
# 第9部分: 执行示例
# ===========================================================

if __name__ == "__main__":
    """主函数 - 执行所有流式处理示例
    
    WHY - 设计思路:
    1. 需要一个统一的入口点来展示所有流式处理示例
    2. 需要以一种有组织的方式呈现不同类型的流式处理模式
    3. 方便用户理解不同示例之间的区别和应用场景
    
    HOW - 实现方式:
    1. 依次调用各个示例函数，先从基础示例开始
    2. 每个示例之间添加分隔符和暂停，便于观察
    3. 捕获可能的异常，确保一个示例的失败不会影响其他示例
    
    WHAT - 功能作用:
    提供一个完整的流式处理技术演示，展示LangGraph中
    从简单到复杂的各种流式处理能力和应用方式
    """
    print("===== LangGraph 流式处理与实时反馈示例 =====\n")
    
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
        print("通过这些示例，您应该已经了解了LangGraph中的各种流式处理方式")
        print("从基本状态流、事件流、到字符级流和回调监控，可以根据需求选择合适的方式")
        
    except Exception as e:
        print(f"\n执行过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc() 