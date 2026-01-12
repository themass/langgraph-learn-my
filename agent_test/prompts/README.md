# Prompt 模板配置

本目录包含所有推理范式的 Prompt 模板配置，采用独立的配置文件管理，避免代码拼接，提高可读性和可维护性。

## 📁 目录结构

```
prompts/
├── __init__.py                    # 模块初始化文件
├── cot_prompts.py                 # Chain-of-Thought 推理范式的 Prompt 模板 ✅
├── react_prompts.py               # ReAct 推理范式的 Prompt 模板 ✅
├── tot_prompts.py                 # Tree of Thoughts 推理范式的 Prompt 模板 ✅
├── self_consistency_prompts.py    # Self-Consistency 推理范式的 Prompt 模板 ✅
├── self_reflection_prompts.py     # Self-Reflection 推理范式的 Prompt 模板 ✅
└── README.md                      # 本文件
```

## 🎯 设计原则

1. **分离关注点**: Prompt 模板与业务逻辑分离
2. **完整模板**: 每个 Prompt 都是完整的、可读的模板，避免代码拼接
3. **格式化函数**: 提供格式化函数处理动态内容
4. **易于维护**: 集中管理，方便修改和优化

## 📝 使用示例

### CoT Prompt 使用

```python
from prompts.cot_prompts import (
    COT_SYSTEM_PROMPT,
    format_analyze_prompt,
    format_reasoning_prompt,
    format_conclude_prompt
)

# 使用 System Prompt
system_prompt = COT_SYSTEM_PROMPT

# 格式化分析节点 Prompt
analyze_prompt = format_analyze_prompt(question="问题内容")

# 格式化推理节点 Prompt
reasoning_prompt = format_reasoning_prompt(
    question="问题内容",
    context="已有推理步骤",
    current_step=1,
    max_steps=3,
    remaining_steps=2,
    is_last_step=False
)

# 格式化结论节点 Prompt
conclude_prompt = format_conclude_prompt(
    question="问题内容",
    context="完整推理过程"
)
```

## 🔧 添加新的 Prompt 模板

1. 在 `prompts/` 目录下创建新的 Python 文件（如 `xxx_prompts.py`）
2. 定义完整的 Prompt 模板字符串
3. 提供格式化函数处理动态内容
4. 在 `__init__.py` 中导出

示例：

```python
# prompts/xxx_prompts.py

XXX_SYSTEM_PROMPT = """完整的 System Prompt 内容...
"""

XXX_USER_PROMPT_TEMPLATE = """完整的 User Prompt 模板...
{placeholder1}
{placeholder2}
"""

def format_xxx_prompt(param1: str, param2: str) -> str:
    """格式化 XXX Prompt"""
    return XXX_USER_PROMPT_TEMPLATE.format(
        placeholder1=param1,
        placeholder2=param2
    )
```

## ✅ 优势

- ✅ **可读性强**: Prompt 模板完整、清晰，易于阅读和理解
- ✅ **易于维护**: 集中管理，修改 Prompt 不需要改动业务代码
- ✅ **避免拼接**: 使用格式化函数，避免代码中的字符串拼接
- ✅ **类型安全**: 格式化函数提供类型提示，减少错误
- ✅ **可复用**: Prompt 模板可以在不同地方复用
