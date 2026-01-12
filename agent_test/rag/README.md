# 生产级 RAG 模块

## 📋 概述

本模块实现了生产级的 RAG (Retrieval-Augmented Generation) 系统，支持多种 RAG 模式：
- **基础 RAG**: 向量检索 + LLM 生成
- **Agentic RAG**: 智能路由、多步检索、查询重写
- **LLM RAG**: 使用 LLM 进行检索和生成

## 🎯 核心功能

### 1. 基础 RAG (Basic RAG)

最简单的 RAG 实现，适合大多数场景。

**特点**:
- 向量相似度检索
- 基于检索结果生成答案
- 返回答案、来源、置信度

**使用示例**:
```python
from rag import BasicRAG

rag = BasicRAG()
result = rag.query("什么是RAG？")

print(result["answer"])
print(result["sources"])
print(result["confidence"])
```

### 2. Agentic RAG

智能 RAG 模式，使用 LLM 来决定检索策略。

**特点**:
- **查询重写**: 自动重写查询以提高检索准确性
- **智能路由**: 决定是否需要进一步检索
- **多步检索**: 最多3轮检索，逐步获取更精确的信息
- **自动去重**: 自动去除重复文档
- **相关性排序**: 按相关性排序返回结果

**使用示例**:
```python
from rag import AgenticRAG

rag = AgenticRAG()
result = rag.query("Agentic RAG和普通RAG有什么区别？")

print(f"检索轮次: {result['iterations']}")
print(f"检索历史: {result['retrieval_history']}")
print(f"答案: {result['answer']}")
```

**工作流程**:
```
查询 → 查询重写 → 智能路由 → 检索 → 评估 → [继续检索?] → 生成答案
```

### 3. LLM RAG

使用 LLM 本身进行检索和生成。

**特点**:
- **LLM 生成查询**: 使用 LLM 生成多个查询变体
- **LLM 评估相关性**: 使用 LLM 评估文档相关性
- **智能过滤**: 只返回高相关性文档

**使用示例**:
```python
from rag import LLMRAG

rag = LLMRAG()
result = rag.query("如何使用向量数据库进行检索？")

print(result["answer"])
print(result["retrieved_docs"])
```

## 🔧 工具函数

### rag_tool

可用于 ReAct 等模式的工具函数。

```python
from rag import rag_tool

# 基础 RAG
result = rag_tool("查询内容", mode="basic")

# Agentic RAG
result = rag_tool("查询内容", mode="agentic")

# LLM RAG
result = rag_tool("查询内容", mode="llm")
```

## 📊 模拟向量数据库

### MockVectorDB

模拟向量数据库，用于演示和测试。

**特点**:
- 简单的关键词匹配模拟相似度搜索
- 支持添加文档
- 返回文档和相似度分数

**替换为真实向量数据库**:

```python
from rag import BasicRAG
from your_vector_db import YourVectorDB

# 替换向量数据库
vector_db = YourVectorDB()
rag = BasicRAG(vector_db=vector_db)
```

## 🎨 集成示例

### 与 CoT 生产级 Demo 集成

```python
from rag import rag_tool

# 在节点中使用 RAG
def query_knowledge_base_node(state):
    question = state["question"]
    
    # 使用 RAG 检索
    rag_result = rag_tool(question, mode="agentic")
    
    # 处理 RAG 结果
    retrieved_docs = rag_result.get("retrieved_docs", [])
    # ...
```

### 与 ReAct 集成

```python
from rag import rag_tool

# 在工具列表中添加 RAG
AVAILABLE_TOOLS = {
    "rag_search": Tool(
        "rag_search",
        "使用RAG检索相关信息",
        lambda query, mode="agentic": rag_tool(query, mode)
    ),
    # ... 其他工具
}
```

## 📈 性能对比

| 模式 | 检索轮次 | 查询重写 | 智能路由 | 适用场景 |
|------|---------|---------|---------|---------|
| 基础 RAG | 1轮 | ❌ | ❌ | 简单查询 |
| Agentic RAG | 1-3轮 | ✅ | ✅ | 复杂查询 |
| LLM RAG | 1轮 | ✅ | ❌ | 需要LLM评估 |

## 🔍 查询重写示例

Agentic RAG 会自动重写查询：

**原始查询**: "RAG是什么？"

**重写后**:
- "RAG检索增强生成技术"
- "Retrieval-Augmented Generation"
- "RAG系统的工作原理"

## 🎯 最佳实践

1. **简单查询**: 使用基础 RAG
2. **复杂查询**: 使用 Agentic RAG
3. **需要高精度**: 使用 LLM RAG
4. **生产环境**: 替换 MockVectorDB 为真实向量数据库

## 📝 扩展开发

### 添加新的 RAG 模式

```python
class CustomRAG:
    def __init__(self, vector_db=None):
        self.vector_db = vector_db or MockVectorDB()
        self.llm = get_llm()
    
    def query(self, query: str) -> Dict[str, Any]:
        # 实现自定义 RAG 逻辑
        pass
```

### 自定义向量数据库

```python
class CustomVectorDB:
    def similarity_search(self, query: str, top_k: int = 3):
        # 实现向量检索逻辑
        pass
```

## 🐛 故障排查

### 问题：检索结果为空

**解决方案**:
1. 检查向量数据库是否有文档
2. 尝试使用查询重写
3. 降低相似度阈值

### 问题：检索结果不相关

**解决方案**:
1. 使用 Agentic RAG 的查询重写功能
2. 增加检索轮次
3. 使用 LLM RAG 的 LLM 评估功能

## 📚 参考资料

- [Agentic RAG](https://blog.langchain.dev/agentic-rag/)
- [LLM RAG](https://arxiv.org/abs/2312.10997)
- [RAG 最佳实践](https://www.pinecone.io/learn/retrieval-augmented-generation/)
