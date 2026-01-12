# Tree of Thoughts (ToT) 思维树实现总结

## 📋 概述

**文件名称**：`03_tot_tree_of_thoughts.py`  
**推理范式**：Tree of Thoughts (ToT)  
**实现级别**：基础演示版  
**节点数量**：3 个核心节点  
**代码行数**：约 370 行

---

## 🎯 核心思想

**ToT 是什么？**

Tree of Thoughts (思维树) 是一种探索式推理方法，通过构建搜索树来解决问题：
- 生成多个候选推理路径
- 评估每个路径的质量
- 选择最优路径继续扩展
- 重复直到找到最佳解决方案

**与其他范式的区别：**

| 特征 | CoT | ReAct | ToT |
|------|-----|-------|-----|
| **推理方式** | 线性推理 | 循环（Think-Act-Observe） | 树状搜索 |
| **路径数量** | 单一路径 | 单一路径 | 多路径探索 |
| **评估机制** | 逐步验证 | 观察反馈 | 路径评分 |
| **适用场景** | 复杂推理 | 工具交互 | 需要探索多种可能性 |

---

## 🏗️ 节点结构（3 节点）

```
         START
           ↓
    ┌──────────────┐
    │ 1. Generate  │ ←──┐
    │ (生成路径)    │    │
    └──────┬────────┘    │
           │             │
           ↓             │
    ┌──────────────┐    │
    │ 2. Evaluate  │    │
    │ (评估路径)    │    │
    └──────┬────────┘    │
           │             │
           ↓             │
    ┌──────────────┐    │
    │ 3. Expand    │    │
    │ (扩展路径)    │    │
    └──────┬────────┘    │
           │             │
           ↓             │
     (条件判断)          │
      /       \          │
   继续?     完成?       │
    /           \        │
   Yes          No       │
    └───────────┘        │
           │             │
           └─────────────┘
           ↓
          END
```

---

## 📝 详细节点分析

### 1️⃣ **生成路径节点** (`generate_paths_node`)

**功能：**
- 生成 3-5 个不同的推理路径
- 每个路径有明确的推理方向
- 包含具体的步骤和假设

**输入：**
- `question`: 原始问题
- `existing_paths`: 已有的路径（用于避免重复）
- `depth`: 当前搜索深度

**输出：**
- `paths`: 新生成的路径列表

**路径数据结构：**
```python
{
    "path_id": 1,                    # 路径ID
    "direction": "从用户体验角度分析",  # 推理方向
    "steps": [                       # 具体步骤
        "分析用户需求",
        "识别痛点",
        "提出解决方案"
    ],
    "assumptions": [                 # 假设条件
        "用户熟悉基本操作",
        "系统响应时间正常"
    ],
    "depth": 0,                      # 当前深度
    "score": None,                   # 评分（稍后填充）
    "evaluation": None               # 评估理由（稍后填充）
}
```

**Prompt 策略：**
```
请生成3-5个不同的推理路径或解决思路。每个路径应该：
1. 有明确的推理方向
2. 有具体的步骤
3. 有合理的假设
```

**LLM 温度设置：** `0.7`（较高，增加多样性）

---

### 2️⃣ **评估路径节点** (`evaluate_paths_node`)

**功能：**
- 评估每个候选路径的质量
- 给每个路径打分（0-10分）
- 选择最优路径继续扩展

**输入：**
- `question`: 原始问题
- `paths`: 所有候选路径

**输出：**
- `paths`: 更新后的路径（包含评分和评估理由）
- `current_path_id`: 选中的最佳路径ID

**评估维度：**
1. **逻辑严密性** - 推理是否合理
2. **可行性** - 是否可以实际执行
3. **解决潜力** - 是否能解决问题

**评估结果示例：**
```python
{
    "evaluations": [
        {
            "path_id": 1,
            "score": 8,
            "reasoning": "逻辑清晰，步骤可行",
            "feasibility": "高",
            "potential": "很有希望解决问题"
        },
        {
            "path_id": 2,
            "score": 6,
            "reasoning": "思路新颖但步骤不够具体",
            "feasibility": "中",
            "potential": "需要进一步细化"
        }
    ],
    "best_path_id": 1  # 选择评分最高的路径
}
```

**LLM 温度设置：** `0.3`（较低，保持客观评估）

---

### 3️⃣ **扩展路径节点** (`expand_path_node`)

**功能：**
- 基于最佳路径继续深入推理
- 生成更详细的答案
- 评估信心程度

**输入：**
- `question`: 原始问题
- `current_path_id`: 选中的路径ID
- `paths`: 所有路径信息

**输出：**
- `best_answer`: 最终答案
- `depth`: 更新后的深度

**Prompt 策略：**
```
请基于这个路径继续深入推理，给出更详细的答案。

当前最佳路径：
方向：{direction}
步骤：{steps}

返回JSON格式：
{
  "answer": "最终答案",
  "reasoning": "推理过程",
  "confidence": "信心程度（高/中/低）"
}
```

**LLM 温度设置：** `0.3`（生成稳定答案）

---

## 🔄 工作流程详解

### 完整执行流程

```
1. 初始化
   ├─ question: "如何提高团队工作效率？"
   ├─ paths: []
   ├─ depth: 0
   └─ best_answer: None

2. 第一轮生成（深度 0）
   └─ Generate → 生成 3-5 条路径
       ├─ 路径1: "从流程优化角度"
       ├─ 路径2: "从工具使用角度"
       └─ 路径3: "从团队协作角度"

3. 评估路径
   └─ Evaluate → 评估所有路径
       ├─ 路径1: 8分（最优）
       ├─ 路径2: 7分
       └─ 路径3: 6分

4. 扩展最优路径
   └─ Expand → 基于路径1深入推理
       └─ 生成详细答案

5. 条件判断
   ├─ 如果 depth < 3 且 best_answer 为空 → 返回 Generate（继续探索）
   └─ 否则 → 结束
```

### 迭代示例

**第一次迭代：**
- 生成：3条初始路径
- 评估：选择最佳路径（路径1）
- 扩展：基于路径1推理

**第二次迭代（如果需要）：**
- 生成：基于路径1生成3条细化路径
- 评估：选择最佳细化路径
- 扩展：生成更详细答案

**终止条件：**
- `depth >= 3`（最多3层深度）
- `best_answer` 存在（已找到答案）

---

## 📊 状态管理

### ToTState 结构

```python
class ToTState(TypedDict):
    """ToT 状态"""
    question: str                    # 原始问题
    paths: List[Dict[str, Any]]      # 所有路径（包含历史）
    current_path_id: Optional[int]   # 当前选择的路径ID
    depth: int                       # 搜索深度（0-3）
    best_answer: Optional[str]       # 最佳答案
    finished: bool                   # 是否完成
```

### 状态演变示例

**初始状态：**
```python
{
    "question": "如何提高团队工作效率？",
    "paths": [],
    "current_path_id": None,
    "depth": 0,
    "best_answer": None,
    "finished": False
}
```

**第一次生成后：**
```python
{
    "question": "如何提高团队工作效率？",
    "paths": [
        {"path_id": 1, "direction": "流程优化", ...},
        {"path_id": 2, "direction": "工具使用", ...},
        {"path_id": 3, "direction": "团队协作", ...}
    ],
    "current_path_id": None,
    "depth": 0,
    "best_answer": None,
    "finished": False
}
```

**评估后：**
```python
{
    "question": "如何提高团队工作效率？",
    "paths": [
        {"path_id": 1, "score": 8, "evaluation": "...", ...},
        {"path_id": 2, "score": 7, "evaluation": "...", ...},
        {"path_id": 3, "score": 6, "evaluation": "...", ...}
    ],
    "current_path_id": 1,  # 选中最佳路径
    "depth": 0,
    "best_answer": None,
    "finished": False
}
```

**扩展后（完成）：**
```python
{
    "question": "如何提高团队工作效率？",
    "paths": [...],  # 保留所有路径历史
    "current_path_id": 1,
    "depth": 1,
    "best_answer": "通过流程优化...",
    "finished": True
}
```

---

## 🎨 Prompt 设计

### Prompt 配置文件

**文件**：`agent_test/prompts/tot_prompts.py`

### 三套 Prompt 模板

#### 1. System Prompt

```
你是一个使用思维树(Tree of Thoughts)方法解决问题的专家。

工作流程：
1. 生成多个候选推理路径
2. 评估每个路径的质量和可行性
3. 选择最有希望的路径继续扩展
4. 重复直到找到解决方案
```

#### 2. Generate Prompt（生成路径）

```
问题：{question}
当前状态：{current_state}
已有路径：{existing_paths}

请生成3-5个不同的推理路径或解决思路。
每个路径应该：
1. 有明确的推理方向
2. 有具体的步骤
3. 有合理的假设

返回JSON格式：
{"paths": [{"path_id": 1, "direction": "...", "steps": [...], "assumptions": [...]}]}
```

#### 3. Evaluate Prompt（评估路径）

```
问题：{question}
候选路径：{paths}

请评估每个路径的质量，返回JSON格式：
{
  "evaluations": [
    {"path_id": 1, "score": 8, "reasoning": "...", "feasibility": "...", "potential": "..."}
  ],
  "best_path_id": 1
}
```

#### 4. Expand Prompt（扩展路径）

```
问题：{question}
当前最佳路径：
方向：{direction}
步骤：{steps}

请基于这个路径继续深入推理，给出更详细的答案。
返回JSON格式：
{"answer": "...", "reasoning": "...", "confidence": "高/中/低"}
```

---

## ✅ 优点分析

### 1. **探索多样性**
- ✅ 生成多个候选路径（3-5条）
- ✅ 避免局部最优
- ✅ 增加找到最佳方案的概率

### 2. **系统性评估**
- ✅ 对每个路径进行打分
- ✅ 多维度评估（逻辑、可行性、潜力）
- ✅ 基于客观标准选择最优路径

### 3. **迭代优化**
- ✅ 支持多层深度搜索（最多3层）
- ✅ 每层可以细化前一层的最佳路径
- ✅ 逐步聚焦最优解

### 4. **代码结构清晰**
- ✅ 3 个节点功能明确
- ✅ 状态管理简洁
- ✅ Prompt 独立配置

### 5. **适用场景广泛**
- ✅ 开放性问题（如"如何提高效率？"）
- ✅ 设计类问题（如"设计一个系统"）
- ✅ 策略规划问题（如"制定营销方案"）

---

## ⚠️ 局限性分析

### 1. **计算成本高**
- ⚠️ 每轮生成多个路径（3-5条）
- ⚠️ 需要多次 LLM 调用
- ⚠️ 总调用次数 = 深度 × 3（生成、评估、扩展）

**示例：**
- 深度 1：3 次调用
- 深度 2：6 次调用
- 深度 3：9 次调用

### 2. **搜索深度有限**
- ⚠️ 最大深度仅 3 层
- ⚠️ 对于极其复杂的问题可能不够
- ⚠️ 没有回溯机制

### 3. **路径选择不可逆**
- ⚠️ 选择最优路径后，其他路径被丢弃
- ⚠️ 如果选择错误，无法返回
- ⚠️ 没有 beam search 或保留 top-k 路径

### 4. **缺少剪枝策略**
- ⚠️ 没有提前终止低分路径
- ⚠️ 所有路径都需要评估
- ⚠️ 效率可以进一步优化

### 5. **没有知识增强**
- ⚠️ 不支持 RAG 检索
- ⚠️ 完全依赖 LLM 内部知识
- ⚠️ 可能遗漏重要信息

---

## 🔧 改进建议

### 高优先级改进

#### 1. **增加 Beam Search**
```python
def evaluate_paths_node_with_beam(state: ToTState) -> Dict[str, Any]:
    """保留 top-k 最优路径"""
    k = 3  # 保留前3条路径
    
    # 评估所有路径
    paths_with_scores = sorted(paths, key=lambda p: p.get("score", 0), reverse=True)
    
    # 保留 top-k
    top_k_paths = paths_with_scores[:k]
    
    return {
        "paths": paths,
        "top_k_path_ids": [p["path_id"] for p in top_k_paths]
    }
```

**优点：**
- 保留多个候选方案
- 避免过早收敛
- 可以并行探索

#### 2. **增加剪枝策略**
```python
def should_prune_path(path: Dict, threshold: float = 5.0) -> bool:
    """剪枝低分路径"""
    score = path.get("score", 0)
    return score < threshold

def evaluate_paths_node_with_pruning(state: ToTState) -> Dict[str, Any]:
    """评估并剪枝"""
    # 评估路径
    evaluated_paths = evaluate_paths(paths)
    
    # 剪枝
    valid_paths = [p for p in evaluated_paths if not should_prune_path(p)]
    
    return {"paths": valid_paths, "current_path_id": best_path_id}
```

**优点：**
- 减少无效路径的扩展
- 降低计算成本
- 提高效率

#### 3. **集成 RAG 知识增强**
```python
def generate_paths_node_with_rag(state: ToTState) -> Dict[str, Any]:
    """生成路径前先检索相关知识"""
    question = state["question"]
    
    # RAG 检索
    rag = AgenticRAG()
    knowledge = rag.retrieve(question, max_docs=5)
    
    # 在 prompt 中包含检索到的知识
    human_prompt = format_generate_prompt(
        question=question,
        knowledge=format_knowledge(knowledge),  # 新增
        current_state=f"深度 {depth}",
        existing_paths=paths_text
    )
    
    # ... 生成路径
```

**优点：**
- 基于真实知识生成路径
- 提高路径质量
- 减少幻觉

### 中优先级改进

#### 4. **动态深度控制**
```python
def should_continue_search_dynamic(state: ToTState) -> str:
    """基于置信度动态决定深度"""
    confidence = state.get("confidence", 0.5)
    depth = state.get("depth", 0)
    
    # 高置信度提前终止
    if confidence >= 0.9:
        return "finish"
    
    # 低置信度增加深度
    max_depth = 5 if confidence < 0.6 else 3
    
    if depth >= max_depth:
        return "finish"
    
    return "expand"
```

#### 5. **路径合并机制**
```python
def merge_paths_node(state: ToTState) -> Dict[str, Any]:
    """合并相似的路径"""
    paths = state.get("paths", [])
    
    # 识别相似路径
    similar_groups = find_similar_paths(paths)
    
    # 合并相似路径
    merged_paths = []
    for group in similar_groups:
        merged_path = merge_group(group)
        merged_paths.append(merged_path)
    
    return {"paths": merged_paths}
```

---

## 📈 性能分析

### 时间复杂度

**单层搜索：**
- Generate: O(1) LLM 调用 → 生成 k 条路径
- Evaluate: O(1) LLM 调用 → 评估 k 条路径
- Expand: O(1) LLM 调用 → 扩展 1 条路径

**总时间复杂度：**
- 单层：3 次 LLM 调用
- d 层深度：3d 次 LLM 调用
- 实际耗时：约 10-30 秒/层（取决于 LLM 速度）

### 空间复杂度

**状态存储：**
- 路径数量：k × d（k=3-5, d=0-3）
- 最大路径数：约 15-20 条
- 每条路径：约 500-1000 字符
- 总内存：< 1MB（可忽略）

### 与其他范式对比

| 范式 | LLM 调用次数 | 平均耗时 | 成本 |
|------|-------------|---------|------|
| **CoT** | 3-5 次 | 5-15秒 | 低 |
| **ReAct** | 5-15 次 | 15-45秒 | 中 |
| **ToT** | 9-15 次 | 30-60秒 | 高 |
| **Self-Consistency** | 15-30 次 | 60-90秒 | 很高 |

**ToT 的成本分析：**
- ✅ 比 Self-Consistency 便宜（不需要生成多个完整答案）
- ⚠️ 比 CoT/ReAct 贵（需要生成和评估多个路径）
- ⚠️ 适合高价值、复杂决策场景

---

## 🎯 适用场景

### 最适合的场景

#### 1. **开放性问题**
```
问题：如何提高团队的工作效率？

ToT 优势：
- 可以从多个角度分析（流程、工具、文化）
- 评估每个角度的可行性
- 选择最佳角度深入
```

#### 2. **设计类问题**
```
问题：设计一个用户友好的登录系统需要考虑哪些因素？

ToT 优势：
- 探索多种设计思路（安全性、易用性、美观性）
- 评估每种思路的优劣
- 选择最优设计方案
```

#### 3. **策略规划**
```
问题：为新产品制定营销策略

ToT 优势：
- 生成多种营销策略（社交媒体、内容营销、付费广告）
- 评估每种策略的 ROI
- 选择最优策略组合
```

#### 4. **复杂决策**
```
问题：选择技术栈：React vs Vue vs Angular

ToT 优势：
- 从多个维度分析（学习曲线、生态系统、性能）
- 评估每个选项的总分
- 做出最优决策
```

### 不太适合的场景

#### 1. **简单查询**
```
问题：Python 的版本是多少？

原因：单一答案，不需要多路径探索
推荐：直接查询或 CoT
```

#### 2. **数学计算**
```
问题：计算 123 × 456

原因：只有一个正确答案，不需要探索多种方法
推荐：工具调用或 CoT
```

#### 3. **实时响应**
```
场景：聊天机器人实时对话

原因：ToT 耗时较长（30-60秒），不适合实时场景
推荐：CoT 或简单问答
```

---

## 💡 使用建议

### 1. **合理设置参数**

#### 路径数量
```python
# 简单问题
num_paths = 3

# 中等复杂
num_paths = 5  # 默认

# 高度复杂
num_paths = 7
```

#### 搜索深度
```python
# 快速探索
max_depth = 2

# 标准探索
max_depth = 3  # 默认

# 深度探索
max_depth = 4
```

#### 评分阈值
```python
# 宽松（保留更多路径）
score_threshold = 4.0

# 标准
score_threshold = 5.0  # 默认

# 严格（只保留高分路径）
score_threshold = 6.0
```

### 2. **优化 Prompt**

#### 增加领域知识
```python
TOT_SYSTEM_PROMPT = """你是一个{domain}领域的专家，
使用思维树(Tree of Thoughts)方法解决问题。

领域知识：
{domain_knowledge}

工作流程：
1. 生成多个候选推理路径
...
"""
```

#### 指定评估维度
```python
TOT_EVALUATE_PROMPT_TEMPLATE = """
请从以下维度评估每个路径：
1. 创新性 (0-10)
2. 可行性 (0-10)
3. 成本效益 (0-10)
4. 风险程度 (0-10)

总分 = (创新性 + 可行性 + 成本效益 - 风险程度) / 3
"""
```

### 3. **结合其他范式**

#### ToT + CoT
```python
# 使用 ToT 探索多个方向
# 使用 CoT 在最优方向上深入推理
```

#### ToT + ReAct
```python
# 使用 ToT 规划多个策略
# 使用 ReAct 执行最优策略
```

---

## 📚 运行示例

### 基本运行

```bash
cd agent_test
python 03_tot_tree_of_thoughts.py
```

### 输出示例

```
【问题 1】
问题：如何提高团队的工作效率？

生成的路径：

路径1: 流程优化方向
  步骤: 分析瓶颈, 优化流程, 自动化
  评分: 8/10

路径2: 工具使用方向
  步骤: 选择工具, 培训团队, 持续改进
  评分: 7/10

路径3: 团队协作方向
  步骤: 建立规范, 加强沟通, 激励机制
  评分: 6/10

选择的最佳路径: 路径1

最终答案：通过流程优化提高团队工作效率，
主要包括三个步骤：
1. 识别当前流程中的瓶颈和低效环节
2. 重新设计关键流程，消除不必要的环节
3. 引入自动化工具减少重复劳动
...
```

---

## 🎓 总结

### 核心特点
- ✅ **探索式**：生成多个候选路径
- ✅ **系统性**：客观评估每个路径
- ✅ **优化性**：选择并扩展最优路径
- ✅ **迭代性**：支持多层深度搜索

### 主要优势
- 🎯 适合开放性问题
- 🎯 避免局部最优
- 🎯 系统性评估方案
- 🎯 结果质量高

### 主要劣势
- ⚠️ 计算成本高
- ⚠️ 耗时较长
- ⚠️ 路径选择不可逆
- ⚠️ 缺少知识增强

### 适用场景
- ✅ 开放性问题
- ✅ 设计类问题
- ✅ 策略规划
- ✅ 复杂决策
- ❌ 简单查询
- ❌ 实时响应

### 推荐指数
**⭐⭐⭐⭐☆ 4/5**

适合作为学习 ToT 思想的入门实现，
但在生产环境需要进一步优化（增加 RAG、剪枝、Beam Search 等）。
