from langchain_community.document_loaders import UnstructuredFileLoader
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
# 导入Ollama相关的包
from langchain_community.llms import Ollama

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

# 导入文本
loader = UnstructuredFileLoader("lg_test.txt")
# 将文本转成 Document 对象
document = loader.load()
print(f'documents:{len(document)}')

# 初始化文本分割器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 500,
    chunk_overlap = 0
)

# 切分文本
split_documents = text_splitter.split_documents(document)
print(f'documents:{len(split_documents)}')

# 加载本地Ollama模型，替换原来的OpenAI
# 确保本地已经启动了Ollama服务，并且已经拉取了对应的模型
# 例如: ollama pull llama3 或其他你想使用的模型
llm = Ollama(
    model="llama3",  # 这里替换为你本地已有的模型名称
    base_url="http://localhost:11434"  # Ollama默认地址，如有修改请相应调整
)

# 创建总结链
chain = load_summarize_chain(llm, chain_type="refine", verbose=True)

# 执行总结链，（为了快速演示，只总结前5段）
print("\n开始执行总结链...")
result = chain.run(split_documents[:5])
print("\n总结结果:")
print(result)