# ✅ RAG 模块修复 - ValueError: Single '}' encountered in format string

## 🎉 最终修复完成

**问题已彻底解决！** 程序现在可以完整运行，包括 RAG 检索功能。

---

## 🐛 新发现的问题

### 问题描述

在修复了 `prompts/cot_production_prompts.py` 后，程序在 `query_knowledge_base_node` 中仍然报错：

```
ValueError: Single '}' encountered in format string
During task with name 'query_knowledge_base' and id '...'
```

### 根本原因

**RAG 模块的 prompt 模板也使用了 `{{` 而不是 `{{{{`！**

RAG 模块 (`agent_test/rag/production_rag.py`) 中的所有 JSON 示例都使用了错误的转义格式。

---

## ✅ 修复方案

### 修复的文件

**`agent_test/rag/production_rag.py`**

### 修复的 Prompt 模板

所有 JSON 示例都从 `{{` 改为 `{{{{`：

#### 1. `QUERY_REWRITE_PROMPT`

```python
# 修复前
返回JSON格式：
{{"rewritten_queries": ["重写查询1", "重写查询2", ...], ...}}

# 修复后
返回JSON格式：
{{{{"rewritten_queries": ["重写查询1", "重写查询2", ...], ...}}}}
```

#### 2. `AGENTIC_ROUTING_PROMPT`

```python
# 修复前
返回JSON格式：
{{"needs_retrieval": true/false, ...}}

# 修复后
返回JSON格式：
{{{{"needs_retrieval": true/false, ...}}}}
```

#### 3. `ANSWER_GENERATION_PROMPT`

```python
# 修复前
返回JSON格式：
{{"answer": "答案内容", "sources": [...], ...}}

# 修复后
返回JSON格式：
{{{{"answer": "答案内容", "sources": [...], ...}}}}
```

#### 4. LLM RAG 中的 Prompt

```python
# 修复前
返回JSON格式：
{{"queries": ["查询1", ...], ...}}

# 修复后
返回JSON格式：
{{{{"queries": ["查询1", ...], ...}}}}
```

#### 5. 文档相关性评估 Prompt

```python
# 修复前
返回JSON格式：
{{"relevant_docs": ["文档ID1", ...], ...}}

# 修复后
返回JSON格式：
{{{{"relevant_docs": ["文档ID1", ...], ...}}}}
```

### 删除了多余的转义代码

删除了所有 `re.sub` 转义逻辑，因为模板中已经正确使用了 `{{{{`：

```python
# 删除前
def format_query_rewrite_prompt(query: str, context: str = "") -> str:
    prompt = QUERY_REWRITE_PROMPT.format(query=query, context=context)
    prompt = re.sub(r'(\{[^}]*\})', lambda m: m.group(1).replace('{', '{{').replace('}', '}}'), prompt)  # ← 删除
    return prompt

# 删除后
def format_query_rewrite_prompt(query: str, context: str = "") -> str:
    prompt = QUERY_REWRITE_PROMPT.format(query=query, context=context)
    return prompt  # ← 简化
```

---

## 🧪 测试结果

### 运行测试

```bash
cd agent_test
python3 01_cot_chain_of_thought_production.py
```

### 结果

```
✅ 程序完整运行成功
✅ 没有 ValueError 错误
✅ RAG 模块正常工作：
   - Agentic RAG 多步检索成功
   - 查询重写成功
   - 答案生成成功
✅ 所有节点正常执行：
   - gather_information_node
   - query_knowledge_base_node (包含 RAG 检索)
   - analyze_question_node
   - reasoning_node (3次迭代)
   - conclude_node
   - handle_uncertainty_node
✅ 生成完整的推理结果，包括：
   - 最终答案
   - 推理步骤
   - 实施步骤
   - 局限性
   - 替代路径
   - 置信度评估
```

---

## 📝 修复总结

### 所有修复的文件

1. **`agent_test/prompts/cot_production_prompts.py`** ✅
   - 所有 CoT 节点的 prompt 模板
   - 所有格式化函数的参数转义

2. **`agent_test/rag/production_rag.py`** ✅
   - 所有 RAG 相关的 prompt 模板
   - 删除多余的 `re.sub` 转义代码

3. **`agent_test/01_cot_chain_of_thought_production.py`** ✅
   - 修复 `alternative_paths` 可能为 `None` 的问题

### 修复的 Prompt 模板总数

**CoT 模块**: 5 个模板
- `QUERY_KNOWLEDGE_PROMPT_TEMPLATE`
- `ANALYZE_PROMPT_TEMPLATE`
- `REASONING_PROMPT_TEMPLATE_BASE`
- `CONCLUDE_PROMPT_TEMPLATE`
- `UNCERTAINTY_PROMPT_TEMPLATE`

**RAG 模块**: 5 个模板
- `QUERY_REWRITE_PROMPT`
- `AGENTIC_ROUTING_PROMPT`
- `ANSWER_GENERATION_PROMPT`
- LLM RAG 查询生成 Prompt
- 文档相关性评估 Prompt

**总计**: 10 个模板 ✅

---

## 🎯 经验总结

### 花括号转义的完整规则

**在 Python 中使用 `.format()` + `ChatPromptTemplate` 时**：

1. **变量占位符**: `{variable_name}` → 被 `.format()` 替换为实际值
2. **字面量花括号**: `{{{{` → 经过 `.format()` → `{{` → 被 `ChatPromptTemplate` 识别为字面量 `{`
3. **参数中的 JSON**: 使用 `escape_json_braces()` 转义为 `{{`

**转义流程**:

```
模板中的 JSON 示例: {{{{...}}}}
                 ↓ .format()
                 {{...}}
                 ↓ ChatPromptTemplate
                 ✅ 识别为字面量 JSON

参数中的 JSON: {"key": "value"}
            ↓ escape_json_braces()
            {{"key": "value"}}
            ↓ .format()
            {{"key": "value"}}
            ↓ ChatPromptTemplate
            ✅ 识别为字面量 JSON
```

### 检查清单（扩展版）

- [x] CoT 模块的所有 prompt 模板使用 `{{{{`
- [x] RAG 模块的所有 prompt 模板使用 `{{{{`
- [x] 所有格式化函数的参数都使用 `escape_json_braces()`
- [x] 删除所有多余的 `re.sub` 转义代码
- [x] 使用 `or []` 处理可能为 `None` 的列表参数
- [x] 测试所有功能模块（CoT + RAG）

---

## ✅ 最终状态

**修复完成！所有功能正常！** 🎉🎉🎉

**验证**: 
```bash
cd agent_test
python3 01_cot_chain_of_thought_production.py
```
✅ **成功运行，无错误！**

**修复的文件**:
- `agent_test/prompts/cot_production_prompts.py` ✅
- `agent_test/rag/production_rag.py` ✅
- `agent_test/01_cot_chain_of_thought_production.py` ✅

**相关文档**:
- `agent_test/FIX_VALUEERROR_SINGLE_BRACE.md` (详细修复说明)
- `agent_test/RAG_FIX_SUMMARY.md` (本文档)
