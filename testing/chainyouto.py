import os

from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ChatVectorDBChain, ConversationalRetrievalChain

from langchain_community.chat_models import ChatOllama
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

# 创建测试文档
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

LangGraph的核心概念：
- 节点（Nodes）：执行特定任务的函数
- 边（Edges）：定义节点之间的连接关系
- 状态（State）：在工作流中传递的数据
- 图（Graph）：由节点和边组成的执行流程

LangGraph的优势：
- 更好的状态管理
- 灵活的流程控制
- 可重用的组件
- 更好的调试能力
- 支持复杂的业务逻辑
"""

# 将测试内容写入文件
with open("langgraph_docs.txt", "w", encoding="utf-8") as f:
    f.write(test_content)

print("已创建测试文档: langgraph_docs.txt")

try:
    # 加载本地文档
    print("正在加载文档...")
    loader = TextLoader("langgraph_docs.txt")
    # 将数据转成 document
    documents = loader.load()
    print(f"成功加载文档，获得 {len(documents)} 个文档")

    # 初始化文本分割器
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    # 分割文档
    documents = text_splitter.split_documents(documents)
    print(f"分割后得到 {len(documents)} 个文档片段")

    # 初始化 Ollama embeddings
    print("正在初始化Ollama嵌入模型...")
    embeddings = OllamaEmbeddings(model="llama3")

    # 将数据存入向量存储
    print("正在创建向量存储...")
    vector_store = Chroma.from_documents(documents, embeddings)
    # 通过向量存储初始化检索器
    retriever = vector_store.as_retriever()

    system_template = """
    使用以下上下文来回答用户的问题。
    如果你不知道答案，就说你不知道，不要试图编造答案。请用中文回答。
    -----------
    {question}
    -----------
    {chat_history}
    """

    # 构建初始 messages 列表
    messages = [
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template('{question}')
    ]

    # 初始化 prompt 对象
    prompt = ChatPromptTemplate.from_messages(messages)

    # 初始化问答链
    print("正在初始化问答链...")
    qa = ConversationalRetrievalChain.from_llm(
        ChatOllama(model="llama3", temperature=0.1),
        retriever,
        condense_question_prompt=prompt
    )

    chat_history = []
    print("\n=== LangGraph文档问答系统 ===")
    print("输入 'quit' 退出")
    
    while True:
        question = input('\n问题：')
        if question.lower() == 'quit':
            break
            
        try:
            # 开始发送问题 chat_history 为必须参数,用于存储对话历史
            result = qa({'question': question, 'chat_history': chat_history})
            chat_history.append((question, result['answer']))
            print(f"\n答案：{result['answer']}")
        except Exception as e:
            print(f"处理问题时出错：{e}")

except ImportError as e:
    print(f"导入错误：{e}")
    print("请确保已安装所有必要的依赖包")
except Exception as e:
    print(f"运行错误：{e}")
    print("请检查Ollama服务是否正常运行")