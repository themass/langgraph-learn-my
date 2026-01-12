from langchain_community.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama
from langchain.chains.summarize import load_summarize_chain
from langgraph.graph import StateGraph, END
from typing import Dict, List
from langchain.schema import Document

# 创建测试文件
test_content = """
LangGraph是一个用于构建状态机、聊天机器人和工作流的库。它基于LangChain构建，提供了更强大的状态管理和流程控制能力。

LangGraph的主要特点包括：
1. 状态管理：可以定义和管理复杂的状态结构
2. 流程控制：支持条件分支、循环和递归
3. 节点系统：可以创建可重用的处理节点
4. 事件驱动：支持事件驱动的架构设计
5. 可视化：提供图形化的流程设计界面

LangGraph适用于以下场景：
- 构建复杂的聊天机器人
- 实现多步骤的工作流程
- 创建状态驱动的应用程序
- 设计智能代理系统
- 实现业务流程自动化

使用LangGraph，开发者可以轻松构建复杂的AI应用程序，而无需担心底层的状态管理和流程控制细节。
"""

# 将测试内容写入文件
with open("lg_test.txt", "w", encoding="utf-8") as f:
    f.write(test_content)

print("已创建测试文件: lg_test.txt")

# 定义存储节点：负责加载和分割文档
def store_document_node(state: Dict) -> Dict:
    print("执行存储节点...")

    # 加载文档
    loader = UnstructuredFileLoader(state["file_path"])
    documents = loader.load()
    print(f'原始文档数量: {len(documents)}')

    # 分割文档
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=0
    )
    split_docs = text_splitter.split_documents(documents)
    print(f'分割后的文档数量: {len(split_docs)}')

    # 返回更新后的状态
    return {**state, "documents": split_docs}

# 定义查询节点：负责总结文档内容
def query_document_node(state: Dict) -> Dict:
    print("执行查询节点...")

    # 加载本地Ollama模型
    llm = Ollama(
        model=state["model_name"],
        base_url=state.get("base_url", "http://localhost:11434")
    )

    # 创建总结链
    chain = load_summarize_chain(llm, chain_type="refine", verbose=True)

    # 执行总结（使用前5段文档进行演示）
    summary = chain.run(state["documents"][:5])
    print("文档总结完成")

    # 返回更新后的状态
    return {**state, "summary": summary}

# 创建工作流
def create_document_workflow():
    # 初始化图
    workflow = StateGraph(Dict)

    # 添加节点
    workflow.add_node("store_document", store_document_node)
    workflow.add_node("query_document", query_document_node)

    # 设置流程：存储 -> 查询 -> 结束
    workflow.add_edge("store_document", "query_document")
    workflow.add_edge("query_document", END)

    # 设置入口点
    workflow.set_entry_point("store_document")

    # 编译工作流
    return workflow.compile()

if __name__ == "__main__":
    # 创建工作流
    app = create_document_workflow()

    # 定义输入参数
    input_state = {
        "file_path": "lg_test.txt",
        "model_name": "llama3",  # 替换为你本地的模型名称
        "base_url": "http://localhost:11434"  # Ollama默认地址
    }

    # 运行工作流
    result = app.invoke(input_state)

    # 输出结果
    print("\n===== 文档总结结果 =====")
    print(result["summary"])
