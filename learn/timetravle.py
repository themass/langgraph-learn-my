from typing import TypedDict, List
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver  # 关键导入

# 1. 定义状态
class MyState(TypedDict):
    messages: List[HumanMessage]

# 2. 定义节点
def node1(state: MyState) -> MyState:
    return {**state, "messages": state["messages"] + [HumanMessage(content="节点1执行")]}

def node2(state: MyState) -> MyState:
    return {** state, "messages": state["messages"] + [HumanMessage(content="节点2执行")]}

# 3. 初始化检查点存储
memory = MemorySaver()

# 4. 构建图
graph = StateGraph(MyState)
graph.add_node("node1", node1)
graph.add_node("node2", node2)
graph.add_edge("node1", "node2")
graph.add_edge("node2", END)
graph.set_entry_point("node1")

# 5. 编译图（必须传入checkpointer）
app = graph.compile(checkpointer=memory)  # 启用检查点功能

# 6. 执行图（指定thread_id）
thread_id = "test-thread"
app.invoke(
    {"messages": [HumanMessage(content="初始消息")]},
    config={"configurable": {"thread_id": thread_id}}
)

# 7. 获取检查点信息
# 注意：新版本的LangGraph API可能有所不同
print("图执行完成！")
print("检查点功能已启用，状态已保存到内存中。")

# 尝试获取检查点信息（如果API可用）
try:
    # 获取当前线程的检查点
    checkpoint_info = app.get_state(
        config={"configurable": {"thread_id": thread_id}}
    )
    print(f"\n当前状态: {checkpoint_info}")
except Exception as e:
    print(f"获取检查点信息时出错: {e}")
    print("这可能是因为API版本差异或检查点功能配置问题。")
