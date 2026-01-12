# ReAct 模式生产级实现方案设计

## 📋 概述

基于 ReAct (Reasoning + Acting) 推理范式，设计一个生产级的智能代理系统。

---

## 🎯 核心设计原则

### 1. ReAct 的核心特征
- **Think (思考)**：分析当前状态，决定下一步行动
- **Act (行动)**：执行工具调用或操作
- **Observe (观察)**：观察行动结果，反馈到下一轮思考
- **循环迭代**：持续 Think-Act-Observe 直到任务完成

### 2. 生产级增强要求
- **知识增强**：集成 RAG 检索，获取领域知识
- **策略规划**：提前分析任务，制定执行计划
- **反思机制**：评估执行效果，调整策略
- **错误处理**：工具调用失败时的降级和重试
- **不确定性评估**：评估答案的可靠性

---

## 🏗️ 节点设计（推荐 7-8 个节点）

### **方案 A：标准生产级（7 节点）**

```
┌─────────────────────────────────────────────────────────────┐
│                     ReAct 生产级工作流                        │
└─────────────────────────────────────────────────────────────┘

1. 【任务分析】task_analysis_node
   ↓
2. 【知识准备】knowledge_preparation_node
   ↓
3. 【思考】think_node ←─────────┐
   ↓                            │
4. 【行动】act_node              │
   ↓                            │
5. 【观察与反思】observe_reflect_node
   ↓                            │
   (条件判断) ──────────────────┘
   - 如果需要继续 → 返回到 think_node
   - 如果完成 → 继续
   ↓
6. 【答案生成】answer_generation_node
   ↓
7. 【质量评估】quality_assessment_node
   ↓
   END
```

### **方案 B：完整生产级（8 节点）**

```
┌─────────────────────────────────────────────────────────────┐
│                  ReAct 完整生产级工作流                       │
└─────────────────────────────────────────────────────────────┘

1. 【任务分析】task_analysis_node
   ↓
2. 【策略规划】strategy_planning_node
   ↓
3. 【知识检索】knowledge_retrieval_node
   ↓
4. 【思考】think_node ←─────────────┐
   ↓                                │
5. 【行动】act_node                  │
   ↓                                │
6. 【观察】observe_node              │
   ↓                                │
7. 【反思】reflection_node ──────────┘
   ↓
   (条件判断)
   - 如果需要继续 → 返回到 think_node
   - 如果策略需要调整 → 返回到 strategy_planning_node
   - 如果完成 → 继续
   ↓
8. 【答案生成与验证】answer_validation_node
   ↓
   END
```

---

## 📝 详细节点设计

### 1️⃣ **任务分析节点** (`task_analysis_node`)

**功能：**
- 理解任务需求和目标
- 识别任务领域（医学、法律、编程等）
- 提取关键实体和约束条件
- 确定任务复杂度

**输入：**
- `task`: 原始任务描述

**输出：**
- `domain`: 领域分类
- `task_type`: 任务类型（信息检索、计算、决策等）
- `key_entities`: 关键实体列表
- `constraints`: 约束条件
- `complexity`: 任务复杂度（simple/medium/complex）

**示例：**
```python
def task_analysis_node(state: ReActProductionState) -> Dict[str, Any]:
    """分析任务，提取关键信息"""
    task = state["task"]
    
    # 使用 LLM 分析任务
    prompt = f"""分析以下任务：
    
    任务：{task}
    
    请提取：
    1. 任务领域（医学/法律/编程/通用等）
    2. 任务类型（信息检索/计算/决策/创作等）
    3. 关键实体和概念
    4. 任务约束条件
    5. 任务复杂度评估
    
    返回JSON格式。
    """
    
    # LLM 调用...
    
    return {
        "domain": domain,
        "task_type": task_type,
        "key_entities": entities,
        "constraints": constraints,
        "complexity": complexity
    }
```

---

### 2️⃣ **策略规划节点** (`strategy_planning_node`) [可选]

**功能：**
- 制定执行计划和策略
- 确定需要使用的工具
- 估算执行步骤数
- 设置置信度阈值

**输入：**
- `task`, `domain`, `task_type`, `complexity`

**输出：**
- `strategy`: 执行策略描述
- `recommended_tools`: 推荐工具列表
- `estimated_steps`: 预估步骤数
- `confidence_threshold`: 置信度阈值

**示例：**
```python
def strategy_planning_node(state: ReActProductionState) -> Dict[str, Any]:
    """制定执行策略"""
    # 根据任务类型和复杂度制定策略
    
    if complexity == "simple":
        strategy = "直接检索并回答"
        estimated_steps = 2
    elif complexity == "complex":
        strategy = "分步检索、计算、验证、综合"
        estimated_steps = 5-8
    
    return {
        "strategy": strategy,
        "recommended_tools": recommended_tools,
        "estimated_steps": estimated_steps
    }
```

---

### 3️⃣ **知识检索节点** (`knowledge_retrieval_node`)

**功能：**
- 使用 RAG 检索领域知识
- 支持 Basic RAG / Agentic RAG / LLM RAG
- 查询重写和多步检索
- 知识融合和去重

**输入：**
- `task`, `domain`, `key_entities`

**输出：**
- `relevant_knowledge`: 相关知识列表
- `rag_results`: RAG 检索结果
- `knowledge_confidence`: 知识可信度

**示例：**
```python
def knowledge_retrieval_node(state: ReActProductionState) -> Dict[str, Any]:
    """检索领域相关知识"""
    domain = state["domain"]
    task = state["task"]
    
    # 使用 Agentic RAG 进行智能检索
    agentic_rag = AgenticRAG(knowledge_base=KNOWLEDGE_BASE[domain])
    results = agentic_rag.retrieve(task, max_docs=5)
    
    return {
        "relevant_knowledge": results["documents"],
        "rag_results": results,
        "knowledge_confidence": results.get("confidence", 0.8)
    }
```

---

### 4️⃣ **思考节点** (`think_node`) 【核心】

**功能：**
- 分析当前状态和历史
- 基于知识进行推理
- 决定下一步行动
- 选择合适的工具

**输入：**
- `task`, `relevant_knowledge`, `history`, `observation`

**输出：**
- `thought`: 当前思考内容
- `action`: 下一步行动（工具名称或 "finish"）
- `action_input`: 行动参数
- `reasoning`: 推理依据

**示例：**
```python
def think_node(state: ReActProductionState) -> Dict[str, Any]:
    """ReAct 思考阶段"""
    task = state["task"]
    observation = state.get("observation", "任务刚开始")
    knowledge = state.get("relevant_knowledge", [])
    history = state.get("history", [])
    
    prompt = f"""
    任务：{task}
    
    相关知识：{format_knowledge(knowledge)}
    
    历史记录：{format_history(history)}
    
    当前观察：{observation}
    
    请思考并决定下一步行动：
    1. 如果需要更多信息 → 使用 search 工具
    2. 如果需要计算 → 使用 calculate 工具
    3. 如果信息充足 → 选择 finish 完成任务
    
    返回JSON格式：
    {{
      "thought": "你的思考过程",
      "action": "工具名称或finish",
      "action_input": "工具参数",
      "reasoning": "为什么这样做"
    }}
    """
    
    # LLM 调用并解析...
    
    return {
        "thought": thought,
        "action": action,
        "action_input": action_input,
        "reasoning": reasoning
    }
```

---

### 5️⃣ **行动节点** (`act_node`) 【核心】

**功能：**
- 执行选定的工具调用
- 处理工具执行错误
- 降级策略（工具失败时）
- 记录工具调用历史

**输入：**
- `action`, `action_input`

**输出：**
- `observation`: 行动结果
- `tool_success`: 工具执行是否成功
- `tool_calls`: 工具调用记录

**示例：**
```python
def act_node(state: ReActProductionState) -> Dict[str, Any]:
    """ReAct 行动阶段"""
    action = state.get("action", "finish")
    action_input = state.get("action_input", "")
    
    if action == "finish":
        return {"observation": "准备生成最终答案"}
    
    # 执行工具
    try:
        if action in AVAILABLE_TOOLS:
            tool = AVAILABLE_TOOLS[action]
            observation = tool.execute(**parse_tool_input(action, action_input))
            tool_success = True
        else:
            observation = f"工具 '{action}' 不存在"
            tool_success = False
    except Exception as e:
        observation = f"工具执行失败：{str(e)}"
        tool_success = False
    
    # 记录工具调用
    tool_calls = state.get("tool_calls", [])
    tool_calls.append({
        "tool": action,
        "input": action_input,
        "output": observation,
        "success": tool_success,
        "timestamp": datetime.now().isoformat()
    })
    
    return {
        "observation": observation,
        "tool_success": tool_success,
        "tool_calls": tool_calls
    }
```

---

### 6️⃣ **观察与反思节点** (`observe_reflect_node`)

**功能：**
- 总结行动结果
- 评估执行效果
- 判断是否需要调整策略
- 更新置信度

**输入：**
- `observation`, `tool_success`, `history`, `strategy`

**输出：**
- `reflection`: 反思内容
- `strategy_effective`: 策略是否有效
- `confidence_score`: 当前置信度
- `need_replanning`: 是否需要重新规划

**示例：**
```python
def observe_reflect_node(state: ReActProductionState) -> Dict[str, Any]:
    """观察结果并反思"""
    observation = state["observation"]
    tool_success = state.get("tool_success", True)
    history = state.get("history", [])
    
    prompt = f"""
    观察结果：{observation}
    工具执行：{'成功' if tool_success else '失败'}
    历史记录：{format_history(history)}
    
    请反思：
    1. 这个行动是否有效？
    2. 是否获得了有用的信息？
    3. 当前策略是否需要调整？
    4. 对最终答案的信心程度（0-1）
    5. 是否需要继续行动还是可以得出结论？
    
    返回JSON格式。
    """
    
    # LLM 调用...
    
    return {
        "reflection": reflection,
        "strategy_effective": effective,
        "confidence_score": confidence,
        "need_replanning": need_replan
    }
```

---

### 7️⃣ **答案生成节点** (`answer_generation_node`)

**功能：**
- 基于完整历史生成答案
- 生成实施步骤（如果需要）
- 列出替代方案
- 说明局限性

**输入：**
- `task`, `history`, `relevant_knowledge`, `tool_calls`

**输出：**
- `final_answer`: 最终答案
- `implementation_steps`: 实施步骤（可选）
- `alternative_solutions`: 替代方案（可选）
- `limitations`: 局限性说明

**示例：**
```python
def answer_generation_node(state: ReActProductionState) -> Dict[str, Any]:
    """生成最终答案"""
    task = state["task"]
    history = state.get("history", [])
    knowledge = state.get("relevant_knowledge", [])
    
    prompt = f"""
    基于以下信息生成最终答案：
    
    任务：{task}
    
    完整历史记录：
    {format_complete_history(history)}
    
    相关知识：
    {format_knowledge(knowledge)}
    
    请生成：
    1. 最终答案（清晰、准确）
    2. 实施步骤（如果任务需要执行）
    3. 替代方案（如果有）
    4. 局限性说明（答案的不确定性和前提）
    
    返回JSON格式。
    """
    
    # LLM 调用...
    
    return {
        "final_answer": answer,
        "implementation_steps": steps,
        "alternative_solutions": alternatives,
        "limitations": limitations,
        "finished": True
    }
```

---

### 8️⃣ **质量评估节点** (`quality_assessment_node`)

**功能：**
- 评估答案质量
- 检查答案完整性
- 评估可靠性
- 决定是否需要重试

**输入：**
- `final_answer`, `task`, `confidence_score`

**输出：**
- `quality_score`: 质量评分（0-10）
- `completeness`: 完整性评分
- `reliability`: 可靠性评分
- `needs_retry`: 是否需要重试

**示例：**
```python
def quality_assessment_node(state: ReActProductionState) -> Dict[str, Any]:
    """评估答案质量"""
    final_answer = state["final_answer"]
    task = state["task"]
    confidence = state.get("confidence_score", 0.5)
    
    prompt = f"""
    评估以下答案的质量：
    
    任务：{task}
    答案：{final_answer}
    
    评估维度：
    1. 答案是否直接回答了问题？（完整性）
    2. 答案是否基于可靠的信息？（可靠性）
    3. 答案是否清晰易懂？（清晰度）
    4. 答案是否有遗漏或错误？（准确性）
    
    给出 0-10 的评分和详细反馈。
    
    返回JSON格式。
    """
    
    # LLM 调用...
    
    return {
        "quality_score": score,
        "completeness": completeness,
        "reliability": reliability,
        "assessment_report": report,
        "needs_retry": score < 6.0
    }
```

---

## 🔄 条件边与流程控制

### 1. **主循环条件** (`should_continue`)

```python
def should_continue(state: ReActProductionState) -> str:
    """决定是否继续 Think-Act-Observe 循环"""
    action = state.get("action", "finish")
    
    # 检查是否明确完成
    if action == "finish":
        return "answer_generation"
    
    # 检查是否达到最大迭代次数
    history = state.get("history", [])
    max_iterations = 10  # 最多10轮
    current_iterations = len([h for h in history if h["type"] == "thought"])
    
    if current_iterations >= max_iterations:
        return "answer_generation"
    
    # 检查置信度是否足够
    confidence = state.get("confidence_score", 0.0)
    if confidence >= 0.9:  # 置信度很高，可以提前结束
        return "answer_generation"
    
    # 继续循环
    return "think"
```

### 2. **策略调整条件** (`should_replan`) [可选]

```python
def should_replan(state: ReActProductionState) -> str:
    """决定是否需要重新规划策略"""
    need_replanning = state.get("need_replanning", False)
    strategy_effective = state.get("strategy_effective", True)
    
    # 如果策略无效且尝试次数少于3次
    failed_attempts = state.get("failed_attempts", 0)
    
    if not strategy_effective and failed_attempts < 3:
        return "strategy_planning"
    
    # 继续当前策略
    return "think"
```

### 3. **质量检查条件** (`should_retry`)

```python
def should_retry(state: ReActProductionState) -> str:
    """决定是否需要重试"""
    needs_retry = state.get("needs_retry", False)
    retry_count = state.get("retry_count", 0)
    
    if needs_retry and retry_count < 2:
        # 增加重试计数并返回到知识检索
        return "knowledge_retrieval"
    
    # 接受当前答案
    return END
```

---

## 📊 完整工作流程图

### 方案 A：标准生产级（推荐）

```
                 START
                   ↓
        ┌──────────────────────┐
        │  1. 任务分析          │
        │  (task_analysis)      │
        └──────────────────────┘
                   ↓
        ┌──────────────────────┐
        │  2. 知识准备          │
        │  (knowledge_prep)     │
        └──────────────────────┘
                   ↓
        ┌──────────────────────┐
    ┌─→ │  3. 思考 (think)      │
    │   └──────────────────────┘
    │              ↓
    │   ┌──────────────────────┐
    │   │  4. 行动 (act)        │
    │   └──────────────────────┘
    │              ↓
    │   ┌──────────────────────┐
    │   │  5. 观察与反思        │
    │   │  (observe_reflect)    │
    │   └──────────────────────┘
    │              ↓
    │         (条件判断)
    │        /         \
    │   需要继续?     完成?
    │      /             \
    └─── Yes            No
                         ↓
              ┌──────────────────────┐
              │  6. 答案生成          │
              │  (answer_generation)  │
              └──────────────────────┘
                         ↓
              ┌──────────────────────┐
              │  7. 质量评估          │
              │  (quality_assessment) │
              └──────────────────────┘
                         ↓
                       END
```

---

## 🎨 状态结构设计

```python
class ReActProductionState(TypedDict):
    """ReAct 生产级状态定义"""
    
    # 任务相关
    task: str                                    # 原始任务
    domain: str                                  # 领域分类
    task_type: str                               # 任务类型
    key_entities: List[str]                      # 关键实体
    constraints: List[str]                       # 约束条件
    complexity: str                              # 复杂度
    
    # 策略相关
    strategy: Optional[str]                      # 执行策略
    recommended_tools: Optional[List[str]]       # 推荐工具
    estimated_steps: Optional[int]               # 预估步骤
    
    # 知识相关
    relevant_knowledge: Optional[List[Dict]]     # 相关知识
    rag_results: Optional[List[Dict]]            # RAG 结果
    knowledge_confidence: Optional[float]        # 知识可信度
    
    # ReAct 循环相关
    thought: Optional[str]                       # 当前思考
    action: Optional[str]                        # 当前行动
    action_input: Optional[str]                  # 行动参数
    observation: Optional[str]                   # 观察结果
    reasoning: Optional[str]                     # 推理依据
    
    # 反思相关
    reflection: Optional[str]                    # 反思内容
    strategy_effective: Optional[bool]           # 策略是否有效
    confidence_score: Optional[float]            # 置信度评分
    need_replanning: Optional[bool]              # 是否需要重新规划
    
    # 历史记录
    history: List[Dict[str, Any]]                # 完整历史
    tool_calls: Optional[List[Dict]]             # 工具调用记录
    
    # 答案相关
    final_answer: str                            # 最终答案
    implementation_steps: Optional[List[str]]    # 实施步骤
    alternative_solutions: Optional[List[str]]   # 替代方案
    limitations: Optional[str]                   # 局限性说明
    
    # 质量评估
    quality_score: Optional[float]               # 质量评分
    completeness: Optional[float]                # 完整性
    reliability: Optional[float]                 # 可靠性
    needs_retry: Optional[bool]                  # 是否需要重试
    
    # 控制标志
    finished: bool                               # 是否完成
    retry_count: int                             # 重试次数
    failed_attempts: int                         # 失败尝试次数
```

---

## 💡 关键设计要点

### 1. **与 CoT 的区别**

| 特征 | CoT 模式 | ReAct 模式 |
|------|---------|-----------|
| **核心思想** | 逐步推理，步步深入 | 思考-行动-观察循环 |
| **工具调用** | 可选，嵌入推理中 | 必需，核心组成部分 |
| **循环方式** | 线性推理步骤 | Think-Act-Observe 循环 |
| **适用场景** | 复杂推理、数学证明 | 需要工具交互的任务 |
| **节点数量** | 3-6 个 | 7-8 个 |

### 2. **工具集成的重要性**

ReAct 模式中，工具调用是核心特征：
- 信息检索工具（搜索、RAG）
- 计算工具（数学计算、代码执行）
- 外部 API（天气、数据库查询）
- 专业工具（医学诊断、法律检索）

### 3. **反思机制的价值**

生产级 ReAct 必须包含反思：
- 评估当前策略是否有效
- 判断是否需要调整方法
- 避免无效循环和资源浪费
- 提高最终答案的质量

### 4. **性能优化**

- **最大迭代次数**：10-15 轮
- **置信度阈值**：0.9（提前结束）
- **质量评分阈值**：6.0/10（触发重试）
- **缓存机制**：缓存工具调用结果

---

## 🚀 实现建议

### 1. **最小可行版本（MVP）**

如果资源有限，可以简化为 **5 个节点**：
1. `task_analysis_node` - 任务分析
2. `think_node` - 思考
3. `act_node` - 行动
4. `observe_node` - 观察（简化反思）
5. `answer_generation_node` - 答案生成

### 2. **推荐生产版本**

**7 个节点**（方案 A）是最佳平衡：
- 足够的功能覆盖
- 合理的复杂度
- 易于维护和扩展

### 3. **完整企业版本**

**8 个节点**（方案 B）+ 额外特性：
- 策略规划节点
- 独立的反思节点
- 质量评估和自动重试
- 多层缓存和优化

---

## 📚 参考实现

- **基础版本**：`agent_test/02_react_reasoning_acting.py`（3节点）
- **完整版本**：`learn/自主代理.py`（4节点 + 循环）
- **生产级模板**：参考 `agent_test/01_cot_chain_of_thought_production.py` 的设计模式

---

## ✅ 总结

### 推荐节点数：**7 个节点**

1. 任务分析
2. 知识准备/检索
3. 思考（核心）
4. 行动（核心）
5. 观察与反思
6. 答案生成
7. 质量评估

### 核心流程：
```
分析 → 准备 → [思考 → 行动 → 观察]循环 → 生成 → 评估
```

### 关键特性：
- ✅ 完整的 Think-Act-Observe 循环
- ✅ 知识增强（RAG）
- ✅ 反思机制
- ✅ 质量评估
- ✅ 错误处理和重试
