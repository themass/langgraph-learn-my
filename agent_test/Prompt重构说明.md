# Prompt 重构说明

## 📋 重构目标

将 prompt 格式化函数从主文件中提取出来，统一管理，提高代码可读性和可维护性。

## 🔧 重构内容

### 1. 创建独立的 Prompt 配置文件

**新文件**: `prompts/cot_production_prompts.py`

包含：
- ✅ 所有 Prompt 模板（完整的、可读的模板字符串）
- ✅ 统一的格式化函数
- ✅ 统一的花括号转义处理逻辑

### 2. 主文件简化

**修改前**: `01_cot_chain_of_thought_production.py` 包含：
- 6 个 `format_*_prompt` 函数（~170 行代码）
- 每个函数都有重复的花括号转义逻辑
- Prompt 模板分散在各个函数中

**修改后**: 
- ✅ 只保留业务逻辑
- ✅ 从 `prompts.cot_production_prompts` 导入所有 prompt 相关函数
- ✅ 代码更简洁，关注点更清晰

## 📊 代码对比

### 重构前

```python
# 在主文件中，6个格式化函数，每个都有重复逻辑
def format_gather_info_prompt(question: str, domain: str, context: str) -> str:
    """格式化信息收集 Prompt"""
    # 转义 context 中的花括号
    escaped_context = context.replace('{', '{{').replace('}', '}}')
    
    # 使用4个花括号表示需要转义为2个花括号的JSON示例
    prompt = f"""请分析以下问题...
    {{{{"required_info": [...]}}}}"""
    
    return prompt

# ... 其他5个类似的函数
```

### 重构后

```python
# 主文件：简洁的导入
from prompts.cot_production_prompts import (
    COT_PRODUCTION_SYSTEM_PROMPT,
    format_gather_info_prompt,
    format_query_knowledge_prompt,
    format_analyze_prompt,
    format_reasoning_prompt,
    format_conclude_prompt,
    format_uncertainty_prompt
)

# 使用：直接调用，无需关心实现细节
human_prompt = format_gather_info_prompt(
    question=question,
    domain=domain,
    context=json.dumps(context, ensure_ascii=False)
)
```

## ✅ 重构优势

### 1. **分离关注点**
- Prompt 模板与业务逻辑分离
- 主文件专注于工作流和节点逻辑
- Prompt 文件专注于模板管理

### 2. **提高可读性**
- Prompt 模板是完整的、可读的字符串
- 不需要在代码中拼接字符串
- 更容易理解和修改 Prompt

### 3. **统一管理**
- 所有 Prompt 集中在一个文件中
- 统一的花括号转义处理逻辑
- 统一的格式化函数接口

### 4. **易于维护**
- 修改 Prompt 只需要修改配置文件
- 不需要在主文件中查找和修改
- 更容易进行版本控制和对比

### 5. **代码复用**
- 其他文件也可以导入使用
- 避免重复定义相同的 Prompt
- 保持一致性

## 📁 文件结构

```
agent_test/
├── 01_cot_chain_of_thought_production.py  # 主文件（简化后）
├── prompts/
│   ├── __init__.py
│   ├── cot_prompts.py                      # 基础 CoT Prompt
│   ├── cot_production_prompts.py           # ✨ 生产级 CoT Prompt（新增）
│   ├── react_prompts.py
│   └── ...
└── ...
```

## 🔍 关键改进

### 1. 统一的花括号转义函数

```python
def escape_json_braces(text: str) -> str:
    """转义文本中的花括号，避免 ChatPromptTemplate 误认为是变量"""
    return text.replace('{', '{{').replace('}', '}}')
```

所有格式化函数都使用这个统一的函数，避免重复代码。

### 2. 清晰的 Prompt 模板

```python
GATHER_INFO_PROMPT_TEMPLATE = """请分析以下问题，确定解决问题所需的关键信息：

问题：{question}
领域：{domain}
上下文信息：{context}

请考虑以下方面：
1. 问题的核心是什么
2. 问题属于哪个领域或子领域
3. 解决此类问题通常需要哪些关键信息
4. 问题中可能存在哪些隐含条件或假设

请返回JSON格式：
{{"required_info": [...], "problem_classification": "...", "complexity": ...}}
"""
```

模板是完整的、可读的，不需要在代码中拼接。

### 3. 统一的格式化函数接口

所有格式化函数都遵循相同的模式：
- 接收必要的参数
- 处理参数（转义、格式化）
- 返回格式化后的 prompt 字符串

## 📝 使用示例

### 在主文件中使用

```python
from prompts.cot_production_prompts import (
    COT_PRODUCTION_SYSTEM_PROMPT,
    format_gather_info_prompt,
    format_reasoning_prompt,
    format_conclude_prompt
)

# 在节点中使用
def gather_information_node(state):
    # ...
    human_prompt = format_gather_info_prompt(
        question=question,
        domain=domain,
        context=json.dumps(context, ensure_ascii=False)
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一位专业的问题分析专家..."),
        ("human", human_prompt)
    ])
    # ...
```

## 🎯 设计原则

1. **完整模板**: 每个 Prompt 都是完整的、可读的模板
2. **避免拼接**: 不在代码中拼接字符串
3. **统一处理**: 统一的花括号转义逻辑
4. **易于修改**: 修改 Prompt 只需要修改配置文件
5. **向后兼容**: 函数接口保持不变，不影响现有代码

## ✅ 验证结果

- ✅ 所有格式化函数测试通过
- ✅ 主文件导入成功
- ✅ 代码语法检查通过
- ✅ 功能保持不变，只是代码组织更清晰

## 📈 代码统计

| 指标 | 重构前 | 重构后 | 改进 |
|------|--------|--------|------|
| 主文件行数 | ~1236 | ~1066 | -170 行 |
| Prompt 相关代码 | 分散在主文件 | 集中在配置文件 | ✅ |
| 代码可读性 | 中等 | 高 | ✅ |
| 可维护性 | 中等 | 高 | ✅ |

## 💡 后续建议

1. **其他 Demo 文件**: 可以考虑将其他 demo 文件的 prompt 也提取到配置文件中
2. **Prompt 版本管理**: 可以考虑添加版本号，方便追踪 Prompt 变更
3. **Prompt 测试**: 可以添加 Prompt 格式化的单元测试
4. **文档完善**: 为每个 Prompt 模板添加使用说明和示例
