# 生产级 Demo 集成指南

## 📋 概述

本文档说明如何在生产级 CoT Demo 中集成工具调用和 RAG 模块。

## 🔧 已完成的集成

### 1. RAG 模块 ✅

**位置**: `rag/production_rag.py`

**功能**:
- ✅ 基础 RAG
- ✅ Agentic RAG（智能路由、多步检索、查询重写）
- ✅ LLM RAG
- ✅ 模拟向量数据库

**使用**:
```python
from rag import BasicRAG, AgenticRAG, LLMRAG, rag_tool

# 在节点中使用
rag_result = rag_tool(query, mode="agentic")
```

### 2. 工具定义 ✅

**已添加的工具**:
- `query_rewrite`: 查询重写工具
- `rag_search`: RAG 检索工具
- `calculate`: 数学计算工具
- `get_time`: 获取当前时间工具

### 3. 状态扩展 ✅

**已添加到 `CoTProductionState`**:
- `tool_calls`: 工具调用记录
- `rag_results`: RAG 检索结果

## 📝 集成步骤

### 步骤1: 更新导入

在 `01_cot_chain_of_thought_production.py` 文件开头添加：

```python
from rag import BasicRAG, AgenticRAG, rag_tool
```

### 步骤2: 更新 gather_information_node

在 `gather_information_node` 中添加工具调用逻辑：

```python
def gather_information_node(state: CoTProductionState) -> Dict[str, Any]:
    """信息收集节点 - 分析问题需求，决定是否需要工具和RAG"""
    
    question = state["question"]
    context = state.get("context", {})
    
    # 判断是否需要 RAG
    needs_rag_keywords = ["什么是", "如何", "为什么", "解释", "介绍", "检索", "搜索"]
    use_rag = any(keyword in question for keyword in needs_rag_keywords)
    
    # 判断是否需要工具
    needs_tools = []
    if "计算" in question or any(op in question for op in ["+", "-", "*", "/"]):
        needs_tools.append("calculate")
    if use_rag:
        needs_tools.append("rag_search")
    
    # 执行工具调用
    tool_calls = state.get("tool_calls", [])
    tool_results = {}
    
    for tool_name in needs_tools:
        if tool_name == "rag_search":
            result = rag_tool(question, mode="agentic")
            tool_results[tool_name] = result
            tool_calls.append({
                "tool": tool_name,
                "input": question,
                "output": result.get("answer", "")[:200],
                "timestamp": datetime.now().isoformat()
            })
        # ... 其他工具
    
    # 更新上下文
    context.update({
        "use_rag": use_rag,
        "rag_mode": "agentic",
        "tool_results": tool_results
    })
    
    # ... 原有逻辑
```

### 步骤3: 更新 query_knowledge_base_node

在 `query_knowledge_base_node` 中集成 RAG：

```python
def query_knowledge_base_node(state: CoTProductionState) -> Dict[str, Any]:
    """知识检索节点 - 支持 RAG 和传统知识库"""
    
    question = state["question"]
    context = state.get("context", {})
    use_rag = context.get("use_rag", False)
    rag_results = state.get("rag_results", [])
    
    # 如果启用 RAG，使用 RAG 检索
    if use_rag:
        try:
            rag_result = rag_tool(question, mode="agentic")
            rag_results.append({
                "query": question,
                "mode": "agentic",
                "retrieved_docs": rag_result.get("retrieved_docs", []),
                "answer": rag_result.get("answer", ""),
                "sources": rag_result.get("sources", [])
            })
            
            # 将 RAG 结果转换为知识条目格式
            rag_knowledge = []
            for doc in rag_result.get("retrieved_docs", []):
                rag_knowledge.append({
                    "id": doc.get("id", f"rag-{len(rag_knowledge)}"),
                    "topic": doc.get("metadata", {}).get("category", "RAG检索"),
                    "content": doc.get("content", ""),
                    "relevance_score": doc.get("score", 8.0),
                    "relevance_explanation": "来自RAG检索",
                    "source": "rag"
                })
            
            # 合并 RAG 结果和传统知识库
            knowledge_entries = KNOWLEDGE_BASE.get(domain, KNOWLEDGE_BASE["通用"])
            knowledge_entries = rag_knowledge + knowledge_entries
        except Exception as e:
            print(f"RAG 检索失败: {e}，使用传统知识库")
            knowledge_entries = KNOWLEDGE_BASE.get(domain, KNOWLEDGE_BASE["通用"])
    else:
        knowledge_entries = KNOWLEDGE_BASE.get(domain, KNOWLEDGE_BASE["通用"])
    
    # ... 原有逻辑
    
    return {
        "relevant_knowledge": relevant_knowledge,
        "rag_results": rag_results,
        # ... 其他字段
    }
```

### 步骤4: 更新 Demo 输出

在 `demo_cot_production` 中显示工具调用和 RAG 结果：

```python
def demo_cot_production():
    # ... 原有代码
    
    result = graph.invoke(initial_state)
    
    # 显示工具调用
    if result.get("tool_calls"):
        print("\n【工具调用】")
        for tool_call in result.get("tool_calls", []):
            print(f"  工具: {tool_call['tool']}")
            print(f"  输入: {tool_call['input']}")
            print(f"  输出: {tool_call['output'][:100]}...")
    
    # 显示 RAG 结果
    if result.get("rag_results"):
        print("\n【RAG 检索结果】")
        for rag_result in result.get("rag_results", []):
            print(f"  查询: {rag_result['query']}")
            print(f"  模式: {rag_result['mode']}")
            print(f"  检索到 {len(rag_result['retrieved_docs'])} 个文档")
            print(f"  答案: {rag_result['answer'][:200]}...")
    
    # ... 其他输出
```

## 🎯 使用示例

### 启用 RAG 的查询

```python
initial_state = {
    "question": "什么是RAG？请详细解释。",
    "domain": "计算机",
    "context": {
        "use_rag": True,  # 启用 RAG
        "rag_mode": "agentic"  # 使用 Agentic RAG
    },
    # ... 其他字段
}
```

### 使用工具的计算查询

```python
initial_state = {
    "question": "计算 2+3*4 等于多少？",
    "domain": "通用",
    "context": {},
    # ... 其他字段
}
```

## 📊 功能对比

| 功能 | 基础版本 | 生产级版本 |
|------|---------|-----------|
| 知识库检索 | ✅ | ✅ |
| RAG 检索 | ❌ | ✅ |
| 工具调用 | ❌ | ✅ |
| 查询重写 | ❌ | ✅ |
| 多步检索 | ❌ | ✅ |
| 不确定性评估 | ❌ | ✅ |
| 循环改进 | ❌ | ✅ |

## 🔍 调试技巧

### 查看工具调用记录

```python
result = graph.invoke(initial_state)
print(json.dumps(result.get("tool_calls", []), indent=2, ensure_ascii=False))
```

### 查看 RAG 检索历史

```python
result = graph.invoke(initial_state)
for rag_result in result.get("rag_results", []):
    if "retrieval_history" in rag_result:
        print(f"检索轮次: {rag_result['iterations']}")
        for history in rag_result["retrieval_history"]:
            print(f"  轮次 {history['iteration']}: {len(history['docs'])} 个文档")
```

## ✅ 检查清单

- [ ] 已导入 RAG 模块
- [ ] 已更新状态定义（添加 tool_calls 和 rag_results）
- [ ] 已在 gather_information_node 中添加工具调用逻辑
- [ ] 已在 query_knowledge_base_node 中集成 RAG
- [ ] 已更新 Demo 输出显示工具和 RAG 结果
- [ ] 已测试工具调用功能
- [ ] 已测试 RAG 检索功能

## 📚 相关文档

- [RAG 模块 README](rag/README.md)
- [生产级 Demo 评估](01_cot_chain_of_thought_production_评估.md)
