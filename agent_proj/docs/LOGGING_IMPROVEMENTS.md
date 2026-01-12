# ProAgent 日志优化说明

## 📋 概述

本文档说明 ProAgent 项目的日志优化内容，提供详细的执行跟踪和调试信息。

## ✨ 主要改进

### 1. 创建统一日志系统

**文件**: `agent_proj/logger.py`

#### 核心功能

- **彩色终端输出**: 使用 ANSI 颜色代码区分不同类型的信息
- **结构化日志**: 统一的日志格式和层次结构
- **智能值格式化**: 自动截断长文本，智能显示列表和字典

#### 主要函数

| 函数 | 用途 |
|------|------|
| `log_node_start()` | 记录节点开始执行，显示当前状态 |
| `log_node_input()` | 记录节点输入数据 |
| `log_node_output()` | 记录节点输出数据 |
| `log_node_end()` | 记录节点执行结束和耗时 |
| `log_llm_call()` | 记录 LLM 调用信息（Prompt长度、响应长度） |
| `log_tool_call()` | 记录工具调用信息 |
| `log_error()` | 记录错误信息 |
| `log_decision()` | 记录决策点 |
| `log_workflow_event()` | 记录工作流事件 |
| `log_state_summary()` | 显示完整的状态摘要 |

### 2. 优化 main_local_db.py

#### 工作流事件日志

- ✅ 计划创建事件（显示步骤数和列表）
- ✅ 步骤完成事件（显示进度和状态）
- ✅ 报告生成事件（显示长度和统计）
- ✅ 验证事件（通过/失败）
- ✅ 不确定性评估
- ✅ 反思结果

#### 状态摘要

执行完成后显示：
- 主题
- 步骤进度
- 研究发现数量
- 推理步骤数量
- 报告信息
- 重试次数

### 3. 节点级别日志

#### 已优化节点

##### Planner 节点
- ✅ 节点开始/结束日志
- ✅ LLM 调用日志（Prompt 长度、响应长度）
- ✅ 输出日志（计划步骤数、描述、理由）
- ✅ 执行时间

##### Executor 节点
- ✅ 节点开始/结束日志
- ✅ ReAct 循环日志（每个周期）
- ✅ Think 阶段日志
- ✅ 工具调用日志
- ✅ 观察结果日志
- ✅ 执行时间

## 📊 日志格式示例

### 节点开始

```
================================================================================
▶ 节点开始: Planner
================================================================================
⏱  时间: 2026-01-13 10:30:15
📊 当前状态:
   • topic: 2024年低空经济市场分析
   • current_step: 0
   • total_steps: 0
   • findings_count: 0

📋 当前执行步骤:
   • ID: N/A
   • 描述: N/A
   • 状态: N/A
```

### LLM 调用

```
🤖 LLM 调用 (Planner): system+user Prompt (1250 字符)
🤖 LLM 调用 (Planner): response Prompt (0 字符), 响应: 350 字符
```

### 节点输出

```
📤 节点输出 (Planner):
   • plan_count: 4
   • plan_steps: ["市场规模分析", "竞争格局分析", "趋势分析", "风险评估"]
   • rationale: 系统性分析低空经济市场...
```

### 节点结束

```
✅ 节点完成: Planner (2.35s)
================================================================================
```

### 工具调用

```
🔧 工具调用 (Executor):
   • 工具: search_market_data
   • 输入: "低空经济市场规模 2024"
   • 结果: 根据最新数据...
```

### 工作流事件

```
📝 工作流事件: plan_created
   • 总步骤数: 4
   • 步骤列表: ["市场规模分析", "竞争格局分析", "趋势分析"]

✅ 工作流事件: step_completed
   • 步骤: 1/4
   • 描述: 市场规模分析
   • 状态: completed

📄 工作流事件: report_generated
   • 报告长度: 2500
   • 推理步骤数: 3
   • 研究发现数: 5
```

### 状态摘要

```
================================================================================
📊 状态摘要
================================================================================
   • 主题: 2024年低空经济市场分析
   • 当前步骤: 4/4
   • 研究发现数量: 5
   • 推理步骤数量: 3
   • 是否有报告: 是
   • 报告长度: 2500
   • 重试次数: 0
================================================================================
```

## 🎨 颜色方案

| 颜色 | 用途 |
|------|------|
| 蓝色 (OKBLUE) | 节点开始/结束，边框 |
| 青色 (OKCYAN) | 信息性输出（状态、事件） |
| 绿色 (OKGREEN) | 成功、输入输出 |
| 黄色 (WARNING) | 警告、工具调用 |
| 红色 (FAIL) | 错误 |
| 紫色 (HEADER) | 重要标题 |
| 粗体 (BOLD) | 强调关键值 |

## 🚀 使用示例

### 在节点中添加日志

```python
from agent_proj.logger import log_node_start, log_node_output, log_node_end, log_llm_call
import time

def my_node(state: AgentState) -> Dict:
    start_time = time.time()
    
    # 记录开始
    log_node_start("MyNode", state)
    
    # 记录 LLM 调用
    log_llm_call("MyNode", "system+user", 1500)
    
    # ... 节点逻辑 ...
    
    # 记录输出
    log_node_output("MyNode", {
        "result": "处理结果",
        "count": 10
    })
    
    # 记录结束
    log_node_end("MyNode", time.time() - start_time)
    
    return output
```

### 在工作流中记录事件

```python
from agent_proj.logger import log_workflow_event

log_workflow_event("custom_event", {
    "detail1": "value1",
    "detail2": "value2"
})
```

## 📈 日志级别

### Level 1: 工作流级别（main_local_db.py）
- 工作流事件
- 步骤进度
- 报告生成
- 验证结果
- 状态摘要

### Level 2: 节点级别（各个 node.py）
- 节点开始/结束
- 输入/输出
- 执行时间

### Level 3: 详细级别（节点内部）
- LLM 调用
- 工具调用
- 决策点
- 中间结果

## 🔍 调试技巧

### 1. 快速定位问题节点
查找 "❌ 错误发生" 或 "▶ 节点开始" 后没有对应的 "✅ 节点完成"

### 2. 检查数据流
关注 "📥 节点输入" 和 "📤 节点输出"，确保数据正确传递

### 3. 性能分析
查看每个节点的执行时间（节点结束时显示）

### 4. LLM 调用优化
监控 "🤖 LLM 调用" 的 Prompt 长度，避免超过 token 限制

## 📝 TODO

待添加日志的节点：
- [ ] progress_check.py
- [ ] result_validation.py
- [ ] uncertainty_handling.py
- [ ] reflection.py
- [ ] analyst.py

## 🎯 最佳实践

1. **始终记录节点开始和结束**
   ```python
   log_node_start("NodeName", state)
   # ... 节点逻辑 ...
   log_node_end("NodeName", execution_time)
   ```

2. **记录关键输入输出**
   ```python
   log_node_output("NodeName", {
       "key_field": value,
       "count": len(items)
   })
   ```

3. **记录 LLM 和工具调用**
   ```python
   log_llm_call("NodeName", "type", prompt_length, response_length)
   log_tool_call("NodeName", tool_name, input, result_preview)
   ```

4. **记录决策点**
   ```python
   log_decision("NodeName", "continue", "reason for decision")
   ```

5. **合理使用颜色**
   - 成功: 绿色
   - 警告: 黄色
   - 错误: 红色
   - 信息: 青色

---

**最后更新**: 2026-01-13  
**维护者**: ProAgent Team
