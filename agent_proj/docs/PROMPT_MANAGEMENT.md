# ProAgent Prompt 管理指南

## 📋 概述

本文档说明 ProAgent 项目的 Prompt 管理架构和使用方法。

## 🏗️ 架构设计

### 核心文件

```
agent_proj/
├── prompts.py                    # 统一的 Prompt 管理模块
└── graph/nodes/                  # 各个节点使用 prompts.py
    ├── planner.py
    ├── executor.py
    ├── progress_check.py
    ├── result_validation.py
    ├── uncertainty_handling.py
    ├── reflection.py
    └── analyst.py
```

### 设计原则

1. **集中管理**: 所有 Prompt 模板集中在 `prompts.py`
2. **分离关注点**: Prompt 内容与业务逻辑分离
3. **易于维护**: 修改 Prompt 无需修改节点代码
4. **配置化**: 温度和模型配置统一管理
5. **可复用**: 通过工厂函数生成 Prompt

## 📦 prompts.py 结构

### 1. System Prompts (系统角色定义)

定义各个节点的 AI 角色和能力：

```python
SENIOR_ANALYST_SYSTEM = """You are a Senior Industry Research Analyst..."""
TASK_EXECUTOR_SYSTEM = """你是一个任务执行代理..."""
PROGRESS_EVALUATOR_SYSTEM = """你是计划评估专家..."""
# ... 更多系统 Prompt
```

### 2. User Prompt Templates (用户指令模板)

定义具体的任务指令模板：

```python
PLANNER_USER_PROMPT = """Research Topic: {topic}

Generate a research plan in JSON format ONLY."""

EXECUTOR_THINK_PROMPT = """当前任务: {task_description}

已有观察结果:
{observations}

请输出JSON格式:
{{"thought": "...", "action": "...", "action_input": "..."}}"""
```

### 3. Prompt Factory Functions (工厂函数)

为每个节点提供 Prompt 构建函数：

```python
def get_planner_prompts(topic: str):
    """获取 Planner 节点的 Prompts"""
    return {
        "system": SENIOR_ANALYST_SYSTEM,
        "user": PLANNER_USER_PROMPT.format(topic=topic)
    }

def get_executor_prompts(task_description: str, observations_text: str):
    """获取 Executor 节点的 Prompts"""
    return {
        "system": TASK_EXECUTOR_SYSTEM,
        "user": EXECUTOR_THINK_PROMPT.format(
            task_description=task_description,
            observations=observations_text
        )
    }
```

### 4. Configuration (配置管理)

统一管理模型和温度配置：

```python
DEFAULT_TEMPERATURES = {
    "planner": 0.7,
    "executor": 0.0,
    "progress_check": 0.3,
    # ...
}

DEFAULT_MODELS = {
    "planner": "moonshot-v1-32k",
    "executor": "moonshot-v1-32k",
    # ...
}

def get_node_config(node_name: str) -> dict:
    """获取节点的配置（温度和模型）"""
    return {
        "temperature": DEFAULT_TEMPERATURES.get(node_name, 0.3),
        "model": DEFAULT_MODELS.get(node_name, "moonshot-v1-32k")
    }
```

## 🔧 节点使用示例

### 旧的方式（不推荐）

```python
# planner.py (旧方式)
def planner_node(state: AgentState) -> Dict:
    llm = get_llm(temperature=0.7, model_name="moonshot-v1-32k")
    
    system_prompt = """You are a Senior Industry Research Analyst.
    Your goal is to break down a complex research topic..."""
    
    user_msg = f"Research Topic: {topic}\n\nGenerate a research plan..."
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", user_msg)
    ])
    
    result = (prompt | llm).invoke({})
```

**问题**:
- ❌ Prompt 分散在各个节点文件中
- ❌ 难以统一管理和修改
- ❌ 配置硬编码
- ❌ 不易于版本控制和对比

### 新的方式（推荐）

```python
# planner.py (新方式)
from agent_proj.prompts import get_planner_prompts, get_node_config

def planner_node(state: AgentState) -> Dict:
    # 1. 获取配置
    config = get_node_config("planner")
    llm = get_llm(temperature=config["temperature"], model_name=config["model"])
    
    # 2. 获取 Prompts
    prompts = get_planner_prompts(topic)
    
    # 3. 构建并调用
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompts["system"]),
        ("human", prompts["user"])
    ])
    
    result = (prompt | llm).invoke({})
```

**优势**:
- ✅ Prompt 集中管理
- ✅ 配置统一管理
- ✅ 易于修改和维护
- ✅ 便于版本控制

## 📝 如何添加新节点的 Prompt

### 步骤 1: 在 `prompts.py` 中添加 System Prompt

```python
NEW_NODE_SYSTEM = """你是一个新节点的角色描述。

职责:
1. ...
2. ...

输出格式:
{{"field1": "...", "field2": "..."}}"""
```

### 步骤 2: 添加 User Prompt Template

```python
NEW_NODE_USER_PROMPT = """输入参数: {param1}

其他上下文:
{param2}

请完成任务并输出JSON格式。"""
```

### 步骤 3: 添加工厂函数

```python
def get_new_node_prompts(param1: str, param2: str):
    """获取新节点的 Prompts"""
    return {
        "system": NEW_NODE_SYSTEM,
        "user": NEW_NODE_USER_PROMPT.format(
            param1=param1,
            param2=param2
        )
    }
```

### 步骤 4: 添加配置

```python
DEFAULT_TEMPERATURES = {
    # ... 现有配置 ...
    "new_node": 0.5,
}

DEFAULT_MODELS = {
    # ... 现有配置 ...
    "new_node": "moonshot-v1-32k",
}
```

### 步骤 5: 在节点中使用

```python
# new_node.py
from agent_proj.prompts import get_new_node_prompts, get_node_config

def new_node(state: AgentState) -> Dict:
    config = get_node_config("new_node")
    llm = get_llm(temperature=config["temperature"], model_name=config["model"])
    
    prompts = get_new_node_prompts(param1, param2)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompts["system"]),
        ("human", prompts["user"])
    ])
    
    result = (prompt | llm).invoke({})
    # ...
```

## 🎯 最佳实践

### 1. Prompt 编写规范

- **明确角色**: System Prompt 应清晰定义 AI 的角色和能力
- **结构化输出**: 明确要求 JSON 输出格式，避免额外文字
- **示例引导**: 在复杂任务中提供输出示例
- **约束说明**: 明确说明不要做什么（如：不要添加额外解释）

### 2. 参数化设计

```python
# ✅ 好的设计
PROMPT_TEMPLATE = """任务: {task}
上下文: {context}
要求: {requirements}"""

# ❌ 不好的设计
PROMPT_TEMPLATE = """任务: 固定的任务描述
上下文: 固定的上下文
要求: 固定的要求"""
```

### 3. 版本控制

在修改 Prompt 时，建议：

1. **保留旧版本**: 注释掉旧版本而不是删除
2. **添加版本号**: 在 Prompt 中添加版本标识
3. **记录变更**: 在文档中记录 Prompt 变更历史

```python
# Version 2.0 - 2026-01-12
# 改进: 添加了更明确的 JSON 格式要求
PLANNER_SYSTEM_V2 = """..."""

# Version 1.0 - 2026-01-10 (已废弃)
# PLANNER_SYSTEM_V1 = """..."""
```

### 4. 测试和验证

修改 Prompt 后，务必测试：

```bash
# 运行完整测试
cd agent_proj
python main_local_db.py

# 或运行单元测试（如果有）
pytest tests/test_prompts.py
```

## 📊 当前 Prompt 清单

| 节点 | System Prompt | User Prompt Template | 温度 | 模型 |
|------|--------------|---------------------|------|------|
| Planner | `SENIOR_ANALYST_SYSTEM` | `PLANNER_USER_PROMPT` | 0.7 | moonshot-v1-32k |
| Executor | `TASK_EXECUTOR_SYSTEM` | `EXECUTOR_THINK_PROMPT` | 0.0 | moonshot-v1-32k |
| Progress Check | `PROGRESS_EVALUATOR_SYSTEM` | `PROGRESS_CHECK_PROMPT` | 0.3 | moonshot-v1-32k |
| Result Validation | `QUALITY_ASSESSOR_SYSTEM` | `VALIDATION_PROMPT` | 0.3 | moonshot-v1-32k |
| Uncertainty | `UNCERTAINTY_EXPERT_SYSTEM` | `UNCERTAINTY_PROMPT` | 0.3 | moonshot-v1-32k |
| Reflection | `REFLECTION_EXPERT_SYSTEM` | `REFLECTION_PROMPT` | 0.3 | moonshot-v1-32k |
| Analyst | `TOP_ANALYST_SYSTEM` | `ANALYST_STEP_PROMPT` | 0.4 | moonshot-v1-32k |
| Report Gen | `REPORT_SYNTHESIZER_SYSTEM` | `REPORT_GENERATION_PROMPT` | 0.4 | moonshot-v1-32k |

## 🔍 Prompt 调优建议

### 温度设置指南

- **0.0 - 0.2**: 需要确定性输出的任务（如工具调用、格式化输出）
  - 例如: Executor (0.0)
  
- **0.3 - 0.5**: 需要一定创造性但仍需准确的任务（如评估、验证）
  - 例如: Progress Check (0.3), Reflection (0.3)
  
- **0.6 - 0.8**: 需要创造性和多样性的任务（如规划、报告生成）
  - 例如: Planner (0.7), Analyst (0.4)

### 模型选择指南

- **moonshot-v1-8k**: 适合简单任务，上下文较短
- **moonshot-v1-32k**: 适合复杂任务，需要大量上下文（推荐）
- **moonshot-v1-128k**: 适合超长上下文任务（如果需要）

## 📚 参考资源

- [LangChain Prompt Templates](https://python.langchain.com/docs/modules/model_io/prompts/)
- [OpenAI Best Practices](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic Prompt Engineering](https://docs.anthropic.com/claude/docs/prompt-engineering)

## 🆘 常见问题

### Q1: 如何快速定位某个节点的 Prompt？

**A**: 在 `prompts.py` 中搜索节点名称，或使用工厂函数名称（如 `get_planner_prompts`）。

### Q2: 修改 Prompt 后需要重启服务吗？

**A**: 是的，Python 模块在导入时加载，修改后需要重启。

### Q3: 如何 A/B 测试不同的 Prompt？

**A**: 可以创建多个版本的工厂函数，通过配置切换：

```python
def get_planner_prompts_v1(topic: str):
    return {"system": PLANNER_SYSTEM_V1, "user": ...}

def get_planner_prompts_v2(topic: str):
    return {"system": PLANNER_SYSTEM_V2, "user": ...}

# 在配置中选择版本
PROMPT_VERSION = "v2"
get_planner_prompts = get_planner_prompts_v2 if PROMPT_VERSION == "v2" else get_planner_prompts_v1
```

### Q4: Prompt 太长导致 Token 超限怎么办？

**A**: 
1. 截断上下文（如 `[:2000]`）
2. 使用更大的模型（如 moonshot-v1-128k）
3. 简化 Prompt 内容
4. 分步处理，减少单次上下文

---

**最后更新**: 2026-01-12  
**维护者**: ProAgent Team
