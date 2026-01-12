# ✅ 问题已完全修复 - ValueError: Single '}' encountered in format string

## 🎉 修复总结

经过系统性的修复，`agent_test/01_cot_chain_of_thought_production.py` 脚本现在可以完全正常运行了！

---

## 🐛 原始问题

```
ValueError: Single '}' encountered in format string
During task with name 'query_knowledge_base' and id '...'
During task with name 'reason' and id '...'
During task with name 'conclude' and id '...'
```

---

## 🔍 根本原因分析

### 问题核心

在 Python 中，字符串格式化存在多层嵌套：
1. **f-string 或 `.format()`** 会消耗一层花括号：`{{` → `{`
2. **`ChatPromptTemplate`** 需要 `{{` 来表示字面量的 `{`

这导致了一个转义层级的问题：
- 如果参数包含 JSON（如 `{"key": "value"}`），直接传入会导致 `ChatPromptTemplate` 误认为 `{` 是模板变量
- 如果在模板中使用 `{{`，经过 `.format()` 后会变成 `{`，仍然会导致 `ChatPromptTemplate` 报错

### 正确的转义策略

**两阶段转义**：
1. **参数转义**：对所有包含 JSON 或其他结构化数据的参数使用 `escape_json_braces()` 转换为 `{{`
2. **模板转义**：在模板的 JSON 示例中使用 `{{{{` (4个花括号) 来表示最终的 `{{`

**转义流程**：
```
参数: {"key": "value"}
    ↓ escape_json_braces()
    {{"key": "value"}}
    ↓ .format()
    {{"key": "value"}}
    ↓ ChatPromptTemplate
    ✅ 识别为字面量 JSON，不是模板变量

模板: {{{{...}}}}
    ↓ .format()
    {{...}}
    ↓ ChatPromptTemplate
    ✅ 识别为字面量花括号
```

---

## ✅ 修复方案

### 1. 修复的文件

**`agent_test/prompts/cot_production_prompts.py`**

#### 修复的模板

所有 JSON 示例都从 `{{` 改为 `{{{{`：

```python
# 修复前
QUERY_KNOWLEDGE_PROMPT_TEMPLATE = """...
{{"relevant_entries": [...]}}
"""

# 修复后
QUERY_KNOWLEDGE_PROMPT_TEMPLATE = """...
{{{{"relevant_entries": [...]}}}}
"""
```

**修复的模板列表**：
- `QUERY_KNOWLEDGE_PROMPT_TEMPLATE`
- `ANALYZE_PROMPT_TEMPLATE`
- `REASONING_PROMPT_TEMPLATE_BASE` (via `json_template`)
- `CONCLUDE_PROMPT_TEMPLATE`
- `UNCERTAINTY_PROMPT_TEMPLATE`

#### 修复的格式化函数

所有格式化函数都对参数进行转义：

**1. `format_query_knowledge_prompt`**
```python
def format_query_knowledge_prompt(
    question: str,
    domain: str,
    required_info: str,
    knowledge_text: str
) -> str:
    # ✅ 转义所有可能包含 JSON 的参数
    escaped_required_info = escape_json_braces(required_info)
    escaped_knowledge_text = escape_json_braces(knowledge_text)
    
    prompt = QUERY_KNOWLEDGE_PROMPT_TEMPLATE.format(
        question=question,
        domain=domain,
        required_info=escaped_required_info,
        knowledge_text=escaped_knowledge_text
    )
    
    return prompt
```

**2. `format_analyze_prompt`**
```python
def format_analyze_prompt(question: str, domain: str, knowledge: str) -> str:
    # ✅ 转义 knowledge 参数
    escaped_knowledge = escape_json_braces(knowledge)
    
    prompt = ANALYZE_PROMPT_TEMPLATE.format(
        question=question,
        domain=domain,
        knowledge=escaped_knowledge
    )
    
    return prompt
```

**3. `format_reasoning_prompt`**
```python
def format_reasoning_prompt(...) -> str:
    # ✅ 构建普通 JSON 字符串（不转义）
    if is_last_step:
        json_template = '{"step_name": "...", ...}'
    else:
        json_template = '{"step_name": "...", ...}'
    
    # ✅ 转义 json_template 以便在 .format() 中使用
    escaped_json_template = escape_json_braces(json_template)
    
    prompt = REASONING_PROMPT_TEMPLATE_BASE.format(
        ...,
        json_template=escaped_json_template,
        ...
    )
    
    return prompt
```

**4. `format_conclude_prompt`**
```python
def format_conclude_prompt(
    question: str,
    context: str,
    knowledge: str,
    alternative_paths: str = ""
) -> str:
    # ✅ 转义所有可能包含 JSON 的参数
    escaped_context = escape_json_braces(context)
    escaped_knowledge = escape_json_braces(knowledge)
    escaped_alternative_paths = escape_json_braces(alternative_paths)
    
    # 准备替代路径部分
    alternative_paths_section = ""
    if alternative_paths:
        alternative_paths_section = f"""

替代推理路径：
{escaped_alternative_paths}
"""
    
    prompt = CONCLUDE_PROMPT_TEMPLATE.format(
        question=question,
        context=escaped_context,
        knowledge=escaped_knowledge,
        alternative_paths_section=alternative_paths_section
    )
    
    return prompt
```

**5. `format_uncertainty_prompt`**
```python
def format_uncertainty_prompt(reasoning: str, solution: str) -> str:
    # ✅ 转义参数
    escaped_reasoning = escape_json_braces(reasoning)
    escaped_solution = escape_json_braces(solution)
    
    prompt = UNCERTAINTY_PROMPT_TEMPLATE.format(
        reasoning=escaped_reasoning,
        solution=escaped_solution
    )
    
    return prompt
```

### 2. 修复的主文件

**`agent_test/01_cot_chain_of_thought_production.py`**

修复了一个小的 bug：
```python
# 修复前
alternative_paths = state.get("alternative_paths", [])
# 如果 state 中 alternative_paths 为 None，这里仍然是 None

# 修复后
alternative_paths = state.get("alternative_paths") or []
# 确保 alternative_paths 始终是列表
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
✅ 程序正常运行
✅ 没有 ValueError 错误
✅ 没有 TypeError 错误
✅ 所有节点正常执行：
   - gather_information_node
   - query_knowledge_base_node
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

## 📝 经验总结

### 问题模式

**任何包含 JSON 或其他结构化数据的字符串参数**，在传递给 f-string 或 `.format()` 之前，**都必须转义花括号**。

### 解决方案模板

```python
# 1. 定义转义函数
def escape_json_braces(text: str) -> str:
    """转义 JSON 中的花括号"""
    return text.replace('{', '{{').replace('}', '}}')

# 2. 在模板中使用 4 个花括号表示字面量的 {{
TEMPLATE = """...
JSON 格式：
{{{{"key": "value"}}}}
"""

# 3. 在格式化函数中转义所有参数
def format_prompt(param1: str, param2: str) -> str:
    escaped_param1 = escape_json_braces(param1)
    escaped_param2 = escape_json_braces(param2)
    
    prompt = TEMPLATE.format(
        param1=escaped_param1,
        param2=escaped_param2
    )
    
    return prompt
```

### 检查清单

- [x] 所有 JSON 字符串参数都已转义
- [x] 所有动态生成的内容都已转义
- [x] 所有可能包含 `{}` 的参数都已转义
- [x] 模板中的 JSON 示例使用 `{{{{` 而不是 `{{`
- [x] 使用 `or []` 处理可能为 `None` 的列表参数
- [x] 删除所有残留的调试代码和 `re.sub` 转义逻辑

---

## 🎯 后续建议

### 1. 统一转义处理

创建一个装饰器或统一的 prompt 格式化函数：

```python
def safe_format_prompt(template: str, **kwargs) -> str:
    """安全地格式化 prompt，自动转义所有参数"""
    escaped_kwargs = {
        key: escape_json_braces(str(value)) if isinstance(value, (str, dict, list)) else value
        for key, value in kwargs.items()
    }
    return template.format(**escaped_kwargs)
```

### 2. 添加单元测试

```python
def test_format_query_knowledge_prompt():
    """测试带 JSON 的 knowledge_text"""
    knowledge = '{"answer": "test", "sources": ["doc1"]}'
    prompt = format_query_knowledge_prompt(
        question="test",
        domain="test",
        required_info='["info"]',
        knowledge_text=knowledge
    )
    # 不应该抛出 ValueError
    assert prompt is not None
    assert '{{' in prompt  # 确保 JSON 被正确转义
```

### 3. 代码审查要点

在添加新的 prompt 模板时，记得检查：
1. 模板中的 JSON 示例是否使用 `{{{{`？
2. 格式化函数中的参数是否都经过 `escape_json_braces()` 转义？
3. 是否有可能为 `None` 的列表需要使用 `or []`？

---

## ✅ 状态

**修复完成！程序可以正常运行了。** 🎉

**验证**: `python3 01_cot_chain_of_thought_production.py` ✅

**相关文件**:
- `agent_test/prompts/cot_production_prompts.py` ✅
- `agent_test/01_cot_chain_of_thought_production.py` ✅
- `agent_test/FIX_VALUEERROR_SINGLE_BRACE.md` (本文档)
