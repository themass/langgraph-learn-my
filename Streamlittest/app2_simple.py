#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简化版 LangGraph FastAPI 服务
===========================
修复图调用问题，提供稳定的聊天API服务
"""

import os
import traceback

import copy
import time
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
import uuid

# LangGraph相关导入
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import OllamaLLM

# FastAPI相关导入
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# ===========================================================
# 状态定义
# ===========================================================

class ChatState(TypedDict):
    """对话状态定义"""
    messages: List[Dict[str, Any]]  # 消息历史
    metadata: Dict[str, Any]  # 元数据

def initialize_state() -> ChatState:
    """初始化对话状态"""
    session_id = f"session-{int(time.time())}"
    
    return {
        "messages": [
            {"role": "system", "content": "你是一个由LangGraph驱动的AI助手，通过UI界面与用户交流。请提供有帮助、安全且友好的回答。"}
        ],
        "metadata": {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
        }
    }

def get_llm():
    """获取LLM实例"""
    return OllamaLLM(
        model="llama3",
        temperature=0.7,
    )

# ===========================================================
# 节点函数
# ===========================================================

def user_input_node(state: ChatState) -> ChatState:
    """处理用户输入的节点"""
    new_state = copy.deepcopy(state)
    
    # 从状态中获取最新的用户消息
    # 这里假设用户消息已经在状态中
    return new_state

def ai_response_node(state: ChatState) -> ChatState:
    """生成AI响应的节点"""
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
    new_state["messages"].append({"role": "assistant", "content": response.strip() })
    
    # 更新元数据
    new_state["metadata"]["last_updated"] = datetime.now().isoformat()
    
    return new_state

def create_chat_graph():
    """创建对话图"""
    # 创建状态图
    workflow = StateGraph(ChatState)
    
    # 添加节点
    workflow.add_node("user_input", user_input_node)
    workflow.add_node("ai_response", ai_response_node)
    
    # 设置边
    workflow.add_edge("user_input", "ai_response")
    workflow.add_edge("ai_response", END)
    
    # 设置入口点
    workflow.set_entry_point("user_input")
    
    # 编译图
    return workflow.compile()

# ===========================================================
# FastAPI 应用
# ===========================================================

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

# API端点 - 聊天
@app.post("/chat", response_model=MessageResponse)
async def chat(request: MessageRequest):
    # 获取或创建会话
    session_id, state = get_or_create_session(request.session_id)
    
    try:
        # 先将用户消息添加到状态中
        state["messages"].append({"role": "user", "content": request.message})
        state["metadata"]["last_updated"] = datetime.now().isoformat()
        
        # 调用图处理用户输入
        result = graph.invoke(state)
        
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
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"处理请求时出错: {str(e)}")

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

# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# 启动服务器
if __name__ == "__main__":
    print("启动 LangGraph API 服务...")
    print("服务地址: http://localhost:8001")
    print("API文档: http://localhost:8001/docs")
    uvicorn.run("app2_simple:app", host="0.0.0.0", port=8001, reload=True)
