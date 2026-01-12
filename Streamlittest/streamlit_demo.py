#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Streamlit LangGraph 聊天 Demo
===========================
使用 Streamlit 构建前端界面，调用 app2.py 提供的 FastAPI 接口
实现一个完整的聊天应用演示

功能特性:
1. 实时聊天界面
2. 会话管理
3. 流式响应显示
4. 会话历史记录
5. 响应式设计
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime
import uuid

# ===========================================================
# 配置
# ===========================================================

# FastAPI 服务地址
API_BASE_URL = "http://localhost:8001"

# ===========================================================
# 页面配置
# ===========================================================

st.set_page_config(
    page_title="LangGraph 聊天 Demo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===========================================================
# 样式设置
# ===========================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    
    .system-message {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
    }
    
    .message-time {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.5rem;
    }
    
    .session-info {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 0.5rem;
    }
    
    .status-online {
        background-color: #4caf50;
    }
    
    .status-offline {
        background-color: #f44336;
    }
</style>
""", unsafe_allow_html=True)

# ===========================================================
# 工具函数
# ===========================================================

def check_api_status():
    """检查 API 服务状态"""
    try:
        response = requests.get(f"{API_BASE_URL}/docs", timeout=5)
        return response.status_code == 200
    except:
        return False

def send_message(message: str, session_id: str = None, stream: bool = False):
    """发送消息到 API"""
    try:
        url = f"{API_BASE_URL}/chat"
        data = {
            "message": message,
            "session_id": session_id,
            "stream": stream
        }
        
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API 请求失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"发送消息时出错: {str(e)}")
        return None

def get_session_info(session_id: str):
    """获取会话信息"""
    try:
        url = f"{API_BASE_URL}/sessions/{session_id}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

def delete_session(session_id: str):
    """删除会话"""
    try:
        url = f"{API_BASE_URL}/sessions/{session_id}"
        response = requests.delete(url, timeout=10)
        
        if response.status_code == 200:
            return True
        else:
            return False
    except:
        return False

# ===========================================================
# 初始化会话状态
# ===========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "api_status" not in st.session_state:
    st.session_state.api_status = False

# ===========================================================
# 主界面
# ===========================================================

# 标题
st.markdown('<h1 class="main-header">🤖 LangGraph 聊天 Demo</h1>', unsafe_allow_html=True)

# 检查 API 状态
st.session_state.api_status = check_api_status()

# 侧边栏
with st.sidebar:
    st.header("🔧 控制面板")
    
    # API 状态指示器
    status_color = "status-online" if st.session_state.api_status else "status-offline"
    status_text = "在线" if st.session_state.api_status else "离线"
    st.markdown(f'<span class="status-indicator {status_color}"></span>API 状态: {status_text}', unsafe_allow_html=True)
    
    if not st.session_state.api_status:
        st.error("⚠️ 无法连接到 API 服务")
        st.info("请确保 app2.py 正在运行在 http://localhost:8001")
    
    st.divider()
    
    # 会话信息
    st.subheader("📋 会话信息")
    st.write(f"**会话 ID:** {st.session_state.session_id[:8]}...")
    
    if st.session_state.api_status:
        session_info = get_session_info(st.session_state.session_id)
        if session_info:
            st.write(f"**消息数量:** {session_info.get('message_count', 0)}")
            st.write(f"**创建时间:** {session_info.get('metadata', {}).get('created_at', 'N/A')}")
    
    st.divider()
    
    # 操作按钮
    st.subheader("⚙️ 操作")
    
    if st.button("🔄 刷新会话", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()
    
    if st.button("🗑️ 清空对话", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("📊 API 文档", use_container_width=True):
        st.markdown(f"[打开 API 文档]({API_BASE_URL}/docs)")
    
    st.divider()
    
    # 关于信息
    st.subheader("ℹ️ 关于")
    st.write("这是一个使用 LangGraph 和 FastAPI 构建的聊天应用演示。")
    st.write("前端使用 Streamlit，后端使用 FastAPI 提供 API 服务。")

# 主聊天区域
if st.session_state.api_status:
    # 显示聊天历史
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        timestamp = message.get("timestamp", "")
        
        if role == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>👤 用户:</strong><br>
                {content}
                <div class="message-time">{timestamp}</div>
            </div>
            """, unsafe_allow_html=True)
        elif role == "assistant":
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>🤖 AI 助手:</strong><br>
                {content}
                <div class="message-time">{timestamp}</div>
            </div>
            """, unsafe_allow_html=True)
        elif role == "system":
            st.markdown(f"""
            <div class="chat-message system-message">
                <strong>⚙️ 系统:</strong><br>
                {content}
                <div class="message-time">{timestamp}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # 用户输入
    user_input = st.chat_input("请输入您的消息...")
    
    if user_input:
        # 添加用户消息到界面
        user_message = {
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        st.session_state.messages.append(user_message)
        
        # 显示用户消息
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>👤 用户:</strong><br>
            {user_input}
            <div class="message-time">{user_message['timestamp']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 发送消息到 API
        with st.spinner("🤖 AI 正在思考中..."):
            response = send_message(user_input, st.session_state.session_id)
            
            if response:
                ai_content = response.get("message", "抱歉，我没有收到有效的响应。")
                ai_message = {
                    "role": "assistant",
                    "content": ai_content,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                }
                st.session_state.messages.append(ai_message)
                
                # 显示 AI 响应
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>🤖 AI 助手:</strong><br>
                    {ai_content}
                    <div class="message-time">{ai_message['timestamp']}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # 自动滚动到底部
        st.rerun()

else:
    # API 离线时的提示
    st.error("🚫 API 服务不可用")
    st.info("""
    **请按以下步骤启动服务:**
    
    1. 确保 app2.py 正在运行
    2. 检查端口 8001 是否可用
    3. 刷新页面重试
    
    **启动命令:**
    ```bash
    python learn/Streamlittest/app2.py
    ```
    """)
    
    # 显示示例对话
    st.subheader("💡 示例对话")
    st.write("当 API 服务可用时，您可以进行以下类型的对话:")
    
    example_messages = [
        "你好，请介绍一下自己",
        "什么是 LangGraph？",
        "请帮我写一个简单的 Python 函数",
        "解释一下人工智能的发展历程",
        "推荐一些学习编程的资源"
    ]
    
    for i, msg in enumerate(example_messages, 1):
        st.write(f"{i}. {msg}")

# 页脚
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8rem;">
    🤖 LangGraph 聊天 Demo | 基于 FastAPI + Streamlit 构建
</div>
""", unsafe_allow_html=True)

