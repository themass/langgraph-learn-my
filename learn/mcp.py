from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel  # 用于请求/响应数据验证

# ------------------------------
# 1. 定义数据模型（请求/响应格式）
# ------------------------------
class MCPRequest(BaseModel):
    """MCP服务请求模型"""
    command: str  # 命令类型：如"query"、"update"、"heartbeat"
    payload: dict  # 命令参数
    client_id: str  # 客户端标识
    sequence: int  # 序列号，用于请求对齐

class MCPResponse(BaseModel):
    """MCP服务响应模型"""
    status: str  # 状态："success"、"error"
    result: Optional[dict] = None  # 成功时的返回数据
    error: Optional[str] = None  # 错误信息
    sequence: int  # 对应请求的序列号
    server_ts: float  # 服务端处理时间戳

# ------------------------------
# 2. 定义服务状态（State）
# ------------------------------
class MCPState(TypedDict):
    """MCP服务状态"""
    request: MCPRequest  # 接收的请求
    response: Optional[MCPResponse]  # 待返回的响应
    processing_log: List[str]  # 处理日志
    client_context: dict  # 客户端上下文（如会话信息）

# ------------------------------
# 3. 定义服务处理节点（Nodes）
# ------------------------------
def parse_request(state: MCPState) -> MCPState:
    """解析请求节点：验证请求格式并提取上下文"""
    log = [f"解析请求: {state['request'].command} (客户端: {state['request'].client_id})"]

    # 提取客户端上下文（实际场景可能从数据库加载）
    client_context = {
        "last_active": "2024-08-21T10:00:00",
        "permissions": ["query", "update"]  # 客户端权限
    }

    return {
        **state,
        "processing_log": state["processing_log"] + log,
        "client_context": client_context
    }

def process_command(state: MCPState) -> MCPState:
    """处理命令节点：根据请求类型执行业务逻辑"""
    request = state["request"]
    log = [f"处理命令: {request.command}"]
    response: Optional[MCPResponse] = None

    try:
        # 检查权限
        if request.command not in state["client_context"]["permissions"]:
            raise PermissionError(f"客户端无{request.command}权限")

        # 模拟不同命令的处理逻辑
        if request.command == "query":
            # 模拟查询操作
            result = {
                "data": f"查询结果: {request.payload.get('key', '未知')}",
                "source": "mock_db"
            }
            response = MCPResponse(
                status="success",
                result=result,
                sequence=request.sequence,
                server_ts=1724236800.0  # 模拟时间戳
            )

        elif request.command == "update":
            # 模拟更新操作
            result = {"updated": request.payload, "rows_affected": 1}
            response = MCPResponse(
                status="success",
                result=result,
                sequence=request.sequence,
                server_ts=1724236801.0
            )

        else:
            raise ValueError(f"不支持的命令: {request.command}")

    except Exception as e:
        # 错误处理
        response = MCPResponse(
            status="error",
            error=str(e),
            sequence=request.sequence,
            server_ts=1724236802.0
        )

    return {
        **state,
        "processing_log": state["processing_log"] + log,
        "response": response
    }

def generate_response(state: MCPState) -> MCPState:
    """生成响应节点：格式化响应数据"""
    log = ["生成最终响应"]
    return {
        **state,
        "processing_log": state["processing_log"] + log
    }

# ------------------------------
# 4. 构建MCP服务图（Graph）
# ------------------------------
def build_mcp_server() -> StateGraph:
    """构建MCP服务状态图"""
    # 初始化状态图
    graph = StateGraph(MCPState)

    # 添加节点
    graph.add_node("parse_request", parse_request)  # 解析请求
    graph.add_node("process_command", process_command)  # 处理命令
    graph.add_node("generate_response", generate_response)  # 生成响应

    # 定义节点流程：解析 → 处理 → 生成响应 → 结束
    graph.add_edge("parse_request", "process_command")
    graph.add_edge("process_command", "generate_response")
    graph.add_edge("generate_response", END)

    # 设置入口点
    graph.set_entry_point("parse_request")

    return graph

# ------------------------------
# 5. 启动服务并测试调用
# ------------------------------
if __name__ == "__main__":
    # 初始化检查点存储（用于维护会话状态）
    memory = MemorySaver()

    # 构建并编译MCP服务
    mcp_graph = build_mcp_server()
    mcp_server = mcp_graph.compile(checkpointer=memory)  # 启用状态持久化

    # 模拟客户端请求
    test_requests = [
        # 合法查询请求
        MCPRequest(
            command="query",
            payload={"key": "user_info"},
            client_id="client_001",
            sequence=1001
        ),
        # 合法更新请求
        MCPRequest(
            command="update",
            payload={"key": "user_info", "value": {"name": "new_name"}},
            client_id="client_001",
            sequence=1002
        ),
        # 非法请求（无权限）
        MCPRequest(
            command="delete",  # 客户端无delete权限
            payload={"key": "user_info"},
            client_id="client_001",
            sequence=1003
        )
    ]

    # 调用MCP服务处理请求
    thread_id = "mcp_session_001"  # 会话ID，用于跟踪客户端会话
    for req in test_requests:
        print(f"\n=== 处理请求 {req.sequence} ===")
        # 发送请求到MCP服务
        final_state = mcp_server.invoke(
            input={
                "request": req,
                "response": None,
                "processing_log": [],
                "client_context": {}
            },
            config={"configurable": {"thread_id": thread_id}}  # 绑定会话
        )

        # 输出服务响应
        response = final_state["response"]
        print(f"服务响应: status={response.status}")
        if response.status == "success":
            print(f"结果: {response.result}")
        else:
            print(f"错误: {response.error}")
        print(f"处理日志: {final_state['processing_log']}")
