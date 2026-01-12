# ProAgent Prompt 快速参考

## 🚀 快速开始

### 导入

```python
from agent_proj.prompts import get_planner_prompts, get_node_config
```

### 使用

```python
# 1. 获取配置
config = get_node_config("planner")
llm = get_llm(temperature=config["temperature"], model_name=config["model"])

# 2. 获取 Prompts
prompts = get_planner_prompts(topic)

# 3. 使用
prompt = ChatPromptTemplate.from_messages([
    ("system", prompts["system"]),
    ("human", prompts["user"])
])
result = (prompt | llm).invoke({})
```

## 📋 所有可用函数

| 函数 | 参数 | 返回 |
|------|------|------|
| `get_node_config(node_name)` | node_name: str | {"temperature": float, "model": str} |
| `get_planner_prompts(topic)` | topic: str | {"system": str, "user": str} |
| `get_executor_prompts(task, obs)` | task: str, obs: str | {"system": str, "user": str} |
| `get_progress_check_prompts(...)` | 5 个参数 | {"system": str, "user": str} |
| `get_validation_prompts(topic, report)` | topic: str, report: str | {"system": str, "user": str} |
| `get_uncertainty_prompts(...)` | 5 个参数 | {"system": str, "user": str} |
| `get_reflection_prompts(...)` | 3 个参数 | {"system": str, "user": str} |
| `get_analyst_step_prompts(...)` | 3 个参数 | {"system": str, "user": str} |
| `get_report_generation_prompts(...)` | 3 个参数 | {"system": str, "user": str} |

## ⚙️ 配置

### 温度设置

| 节点 | 温度 | 说明 |
|------|------|------|
| planner | 0.7 | 需要创造性 |
| executor | 0.0 | 需要确定性 |
| progress_check | 0.3 | 评估任务 |
| validation | 0.3 | 验证质量 |
| uncertainty | 0.3 | 评估不确定性 |
| reflection | 0.3 | 检查推理 |
| analyst | 0.4 | 深度分析 |

### 模型设置

所有节点默认使用 `moonshot-v1-32k`

## 📝 修改 Prompt

1. 打开 `agent_proj/prompts.py`
2. 找到对应的 Prompt 常量（如 `PLANNER_SYSTEM`）
3. 修改内容
4. 保存并重启服务

## 🔍 查找 Prompt

```bash
# 在 prompts.py 中搜索节点名称
grep -i "planner" agent_proj/prompts.py

# 或搜索工厂函数
grep "def get_.*_prompts" agent_proj/prompts.py
```

## 📚 完整文档

详见 `agent_proj/docs/PROMPT_MANAGEMENT.md`

