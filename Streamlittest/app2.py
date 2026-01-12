import os
import copy
import time
from typing import TypedDict, List, Dict, Any, Optional, Generator, Callable
import json
import asyncio
import threading
from datetime import datetime

# LangGraph相关导入
from langgraph.graph import StateGraph, END
# from langgraph.checkpoint import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import OllamaLLM

# =================================================================
# 第1部分: 基础组件 - 对话状态和图定义
# =================================================================

class ChatState(TypedDict):
    """对话状态定义

    WHY - 设计思路:
    1. 需要存储对话历史以保持上下文
    2. 需要记录元数据便于UI展示和状态管理
    3. 需要支持流式输出的状态标记

    HOW - 实现方式:
    1. 使用TypedDict定义类型安全的状态结构
    2. 包含消息历史、元数据和流式输出标记
    3. 设计简洁的结构确保UI层易于使用

    WHAT - 功能作用:
    提供UI层和LangGraph之间的数据交换格式，
    确保数据一致性和类型安全
    """
    messages: List[Dict[str, Any]]  # 消息历史: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    metadata: Dict[str, Any]  # 元数据: 会话ID、时间戳等
    streaming: bool  # 流式输出标记

def initialize_state() -> ChatState:
    """初始化对话状态

    WHY - 设计思路:
    1. 需要为每个用户会话提供初始状态
    2. 初始状态需要包含系统提示和基本元数据

    HOW - 实现方式:
    1. 创建包含空消息列表的状态字典
    2. 添加系统消息设定对话基调
    3. 初始化元数据和流式标记

    WHAT - 功能作用:
    为UI应用提供一致的起点状态，确保每个用户会话
    从相同的初始状态开始

    Returns:
        ChatState: 初始化的状态
    """
    session_id = f"session-{int(time.time())}"

    return {
        "messages": [
            {"role": "system", "content": "你是一个由LangGraph驱动的AI助手，通过UI界面与用户交流。请提供有帮助、安全且友好的回答。"}
        ],
        "metadata": {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
        },
        "streaming": False
    }

def get_llm():
    """获取LLM实例

    WHY - 设计思路:
    1. 需要统一的LLM配置点
    2. 支持不同UI集成方式使用相同的底层模型

    HOW - 实现方式:
    1. 使用OllamaLLM提供本地模型推理
    2. 配置适当的参数确保输出质量

    WHAT - 功能作用:
    提供一个配置好的LLM实例，供各UI集成方式使用，
    确保输出一致性和质量

    Returns:
        OllamaLLM: LLM实例
    """
    return OllamaLLM(
        model="llama3",  # 使用可用的模型
        temperature=0.7,
    )

# =================================================================
# 第2部分: LangGraph核心逻辑 - 节点函数和图构建
# =================================================================

def user_input_node(state: ChatState, message: str) -> ChatState:
    """处理用户输入的节点

    WHY - 设计思路:
    1. 需要将UI层的用户输入整合到LangGraph状态中
    2. 需要维护状态的不变性

    HOW - 实现方式:
    1. 创建状态的深拷贝确保不可变性
    2. 将用户消息添加到消息历史
    3. 更新元数据时间戳

    WHAT - 功能作用:
    处理来自UI层的用户输入，更新状态中的消息历史

    Args:
        state: 当前状态
        message: 用户输入文本

    Returns:
        ChatState: 更新后的新状态
    """
    new_state = copy.deepcopy(state)

    # 添加用户消息
    new_state["messages"].append({"role": "user", "content": message})

    # 更新元数据
    new_state["metadata"]["last_updated"] = datetime.now().isoformat()

    return new_state

def ai_response_node(state: ChatState) -> ChatState:
    """生成AI响应的节点

    WHY - 设计思路:
    1. 需要处理用户输入并生成适当的响应
    2. 需要保持状态的不变性
    3. 响应需要考虑整个对话历史

    HOW - 实现方式:
    1. 创建状态的深拷贝确保不可变性
    2. 从状态中提取对话历史
    3. 调用LLM生成响应
    4. 将响应添加到消息历史

    WHAT - 功能作用:
    根据对话历史生成AI响应，并更新状态

    Args:
        state: 当前状态

    Returns:
        ChatState: 更新后的新状态
    """
    new_state = copy.deepcopy(state)

    # 获取LLM
    llm = get_llm()

    # 提取对话历史
    history = []
    for msg in new_state["messages"]:
        if msg["role"] == "user":
            history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            history.append(AIMessage(content=msg["content"]))
        elif msg["role"] == "system":
            history.append(SystemMessage(content=msg["content"]))

    # 生成AI响应
    response = llm.invoke(history)

    # 添加到消息历史
    new_state["messages"].append({"role": "assistant", "content": response.content})

    # 更新元数据
    new_state["metadata"]["last_updated"] = datetime.now().isoformat()

    return new_state

def create_chat_graph():
    """创建对话图

    WHY - 设计思路:
    1. 需要一个封装对话逻辑的图结构
    2. 图需要支持基本的用户输入和AI响应流程
    3. 图应保持简单以便于UI集成

    HOW - 实现方式:
    1. 创建基于ChatState的StateGraph
    2. 添加处理用户输入和生成AI响应的节点
    3. 定义节点间的连接关系
    4. 设置入口点

    WHAT - 功能作用:
    提供一个封装对话逻辑的图结构，供不同UI框架使用

    Returns:
        StateGraph: 创建的对话图
    """
    # 创建状态图
    workflow = StateGraph(ChatState)

    # 自定义用户输入节点（接收外部消息）
    def process_user_message(state, input_dict):
        return user_input_node(state, input_dict.get("message", ""))

    # 添加节点
    workflow.add_node("user_input", process_user_message)
    workflow.add_node("ai_response", ai_response_node)

    # 设置边缘
    workflow.add_edge("user_input", "ai_response")
    workflow.add_edge("ai_response", END)

    # 设置入口点
    workflow.set_entry_point("user_input")

    # 编译图
    return workflow.compile()
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import uvicorn
import uuid
import json
import asyncio
from typing import Dict, List, Optional, Any
import copy
import time
from datetime import datetime

# 导入上述定义的函数和类
# 确保此脚本中的所有函数和类都已导入
# 在实际使用时可能需要调整导入方式

# 创建FastAPI应用
app = FastAPI(title="LangGraph API服务")

# 启用CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 会话存储
sessions = {}

# API模型定义
class MessageRequest(BaseModel):
    message: str = Field(..., description="用户消息内容")
    session_id: Optional[str] = Field(None, description="会话ID，如果为空则创建新会话")
    stream: bool = Field(False, description="是否启用流式输出")

class MessageResponse(BaseModel):
    session_id: str = Field(..., description="会话ID")
    message: str = Field(..., description="AI响应内容")
    created_at: str = Field(..., description="响应创建时间")

# 会话管理工具
def get_or_create_session(session_id: Optional[str] = None):
    if session_id and session_id in sessions:
        return session_id, sessions[session_id]

    # 创建新会话
    new_session_id = session_id or str(uuid.uuid4())
    sessions[new_session_id] = initialize_state()
    return new_session_id, sessions[new_session_id]

# 创建对话图实例
graph = create_chat_graph()

# API端点 - 非流式消息
@app.post("/chat", response_model=MessageResponse)
async def chat(request: MessageRequest):
    # 获取或创建会话
    session_id, state = get_or_create_session(request.session_id)

    # 处理流式请求
    if request.stream:
        return StreamingResponse(
            stream_response(request.message, state, session_id),
            media_type="text/event-stream"
        )

    # 调用图处理用户输入
    result = graph.invoke(
        {"message": request.message},
        config={"configurable": {"thread_id": session_id}}
    )

    # 更新会话状态
    sessions[session_id] = result

    # 获取AI响应
    ai_response = result["messages"][-1]["content"]
    created_at = datetime.now().isoformat()

    return MessageResponse(
        session_id=session_id,
        message=ai_response,
        created_at=created_at
    )

# 流式响应生成器
async def stream_response(message: str, state: dict, session_id: str):
    # 在实际应用中，这里应该集成LangGraph的流式响应功能
    # 这里为了演示，使用简单的模拟实现

    # 调用图处理用户输入
    result = graph.invoke(
        {"message": message},
        config={"configurable": {"thread_id": session_id}}
    )

    # 更新会话状态
    sessions[session_id] = result

    # 获取AI响应并模拟流式输出
    ai_response = result["messages"][-1]["content"]

    # 每个单词都作为一个流式事件发送
    for word in ai_response.split():
        yield f"data: {json.dumps({'token': word + ' '})}\n\n"
        await asyncio.sleep(0.1)

    # 发送完成事件
    yield f"data: {json.dumps({'token': '', 'finished': True})}\n\n"

# 会话管理端点
@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="会话不存在")

    state = sessions[session_id]
    return {
        "session_id": session_id,
        "metadata": state["metadata"],
        "message_count": len(state["messages"])
    }

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
    return {"status": "success", "message": "会话已删除"}

# 启动服务器
if __name__ == "__main__":
    uvicorn.run("app2:app", host="0.0.0.0", port=8001, reload=True)