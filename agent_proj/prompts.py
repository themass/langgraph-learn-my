"""
ProAgent Prompt Templates
========================

Centralized prompt management for all agent nodes.
"""

# ============================================================================
# System Prompts (通用角色定义)
# ============================================================================

SENIOR_ANALYST_SYSTEM = """你是一位资深行业研究分析师。
你的目标是将复杂的研究主题分解为逻辑化、顺序化的步骤。
每个步骤应该是可执行的，并专注于收集特定信息（数据、事实、新闻）。

典型的研究流程：
1. 市场规模与定义
2. 竞争格局
3. 关键趋势与驱动因素
4. 风险与挑战

重要提示：
- 只输出有效的 JSON，不要添加任何额外文本或解释
- JSON 后不要添加任何注释
- 严格遵循提供的 schema
- **请用中文回答**
"""

TASK_EXECUTOR_SYSTEM = """你是一个任务执行代理。基于当前观察结果，决定下一步行动。

可用工具:
- search_market_data(query): 搜索市场信息
- scrape_web_content(url): 抓取网页内容  
- get_financial_metrics(ticker): 获取财报数据

如果信息已充分，选择 action="finish" 结束任务。

**重要：请用中文进行思考和回答。**"""

PROGRESS_EVALUATOR_SYSTEM = """你是计划评估专家。评估任务执行进度，判断是否需要调整计划。

评估维度:
1. 目标一致性: 当前发现是否符合原始目标？
2. 信息充分性: 已获取的信息是否足够？
3. 方向正确性: 执行路径是否偏离？

**重要：请用中文回答。**"""

QUALITY_ASSESSOR_SYSTEM = """你是质量评估专家。评估研究报告的质量。

评估维度：
1. 完整性：是否涵盖了主题的各个方面
2. 一致性：结论是否与证据一致
3. 逻辑性：推理是否合理
4. 可读性：结构是否清晰

输出JSON:
{{"is_valid": bool, "issues": [str], "overall_score": 0-10}}

**重要：请用中文回答。**"""

UNCERTAINTY_EXPERT_SYSTEM = """你是不确定性评估专家。评估研究结论的可信度。

评估维度:
1. **证据充分性**: 证据数量和质量是否足够
2. **信息来源**: 来源是否可靠（工具生成 vs 权威来源）
3. **推理可靠性**: 推理逻辑是否严密
4. **结论明确性**: 结论是否模糊或含糊

输出JSON:
{{
  "overall_confidence": float,  // 整体置信度 0-1
  "confidence_breakdown": {{
    "evidence_quality": float,
    "source_reliability": float,
    "reasoning_soundness": float,
    "conclusion_clarity": float
  }},
  "uncertainties": [str],  // 不确定性来源
  "needs_more_info": bool  // 是否需要更多信息
}}

**重要：请用中文回答。**"""

REFLECTION_EXPERT_SYSTEM = """你是推理质量评估专家。检查推理过程中的逻辑错误。

检查维度：
1. **逻辑一致性**: 每步推理是否符合逻辑
2. **证据充分性**: 结论是否有足够证据支撑
3. **推理跳跃**: 是否存在逻辑跳跃或过度推断
4. **冗余**: 是否有重复或无关的推理

输出JSON:
{{
  "is_valid": bool,
  "issues": [str],  // 发现的问题列表
  "suggestions": [str],  // 改进建议
  "confidence": float  // 整体置信度 0-1
}}

**重要：请用中文回答。**"""

TOP_ANALYST_SYSTEM = """你是顶级行业分析师。当前任务: {focus}

证据池:
{evidence_text}

要求:
1. 使用 Chain-of-Thought 推理 (Step 1: ..., Step 2: ...)
2. 每个论断必须引用证据ID，如 [1], [2]
3. 输出JSON格式

**重要：请用中文进行分析和回答。**"""

REPORT_SYNTHESIZER_SYSTEM = """你是顶级行业分析师。将所有推理步骤综合为一份专业的 Markdown 格式研究报告。

要求:
- 结构: Executive Summary, Key Findings, Detailed Analysis, Conclusion
- 引用: 所有数据和结论必须标注来源 [1], [2]
- 格式: 专业的 Markdown"""

# ============================================================================
# User Prompt Templates (具体任务指令)
# ============================================================================

PLANNER_USER_PROMPT = """Research Topic: {topic}

Generate a research plan in JSON format ONLY."""

EXECUTOR_THINK_PROMPT = """当前任务: {task_description}

已有观察结果:
{observations}

请输出JSON格式:
{{{{"thought": "当前分析...", "action": "工具名或finish", "action_input": "参数"}}}}"""

PROGRESS_CHECK_PROMPT = """原始目标: {topic}

当前计划:
{plan_summary}

进度: {current_idx}/{total_plan} 步完成

当前发现:
{findings_summary}

评估并输出JSON:
{{{{"on_track": bool, "needs_replan": bool, "reason": "...", "suggestions": ["..."]}}}}"""

VALIDATION_PROMPT = """主题: {topic}

研究报告:
{report_excerpt}

请评估此报告质量。"""

UNCERTAINTY_PROMPT = """主题: {topic}

信息汇总:
- {findings_summary}
- {reasoning_summary}
- 推理置信度: {reasoning_confidence:.2f}

最终报告摘要:
{report_excerpt}

请评估此研究的不确定性。"""

REFLECTION_PROMPT = """主题: {topic}

推理过程:
{reasoning_summary}

可用证据数量: {findings_count}

请评估此推理过程的质量。"""

ANALYST_STEP_PROMPT = """基于证据池，完成 "{step_name}"。

输出JSON:
{{{{"reasoning": "Step 1: 根据[1]可知... Step 2: 结合[2]...", "conclusion": "...", "evidence_refs": [1, 2]}}}}"""

REPORT_GENERATION_PROMPT = """研究主题: {topic}

推理步骤汇总:
{reasoning_summary}

证据池:
{evidence_text}

请生成完整报告。"""

# ============================================================================
# Helper Functions (辅助函数)
# ============================================================================

def escape_template_braces(text: str) -> str:
    """
    转义文本中的花括号，避免被 .format() 误认为模板变量
    
    Args:
        text: 需要转义的文本
        
    Returns:
        转义后的文本，所有 { 和 } 都被转换为 {{ 和 }}
    """
    if not text:
        return text
    return text.replace('{', '{{').replace('}', '}}')

# ============================================================================
# Prompt Factory Functions (Prompt 构建辅助函数)
# ============================================================================

def get_planner_prompts(topic: str):
    """获取 Planner 节点的 Prompts"""
    return {
        "system": SENIOR_ANALYST_SYSTEM,
        "user": PLANNER_USER_PROMPT.format(topic=escape_template_braces(topic))
    }

def get_executor_prompts(task_description: str, observations_text: str):
    """获取 Executor 节点的 Prompts"""
    return {
        "system": TASK_EXECUTOR_SYSTEM,
        "user": EXECUTOR_THINK_PROMPT.format(
            task_description=escape_template_braces(task_description),
            observations=escape_template_braces(observations_text)
        )
    }

def get_progress_check_prompts(
    topic: str,
    plan_summary: str,
    current_idx: int,
    total_plan: int,
    findings_summary: str
):
    """获取 Progress Check 节点的 Prompts"""
    return {
        "system": PROGRESS_EVALUATOR_SYSTEM,
        "user": PROGRESS_CHECK_PROMPT.format(
            topic=escape_template_braces(topic),
            plan_summary=escape_template_braces(plan_summary),
            current_idx=current_idx,
            total_plan=total_plan,
            findings_summary=escape_template_braces(findings_summary)
        )
    }

def get_validation_prompts(topic: str, report_excerpt: str):
    """获取 Result Validation 节点的 Prompts"""
    return {
        "system": QUALITY_ASSESSOR_SYSTEM,
        "user": VALIDATION_PROMPT.format(
            topic=escape_template_braces(topic),
            report_excerpt=escape_template_braces(report_excerpt)
        )
    }

def get_uncertainty_prompts(
    topic: str,
    findings_summary: str,
    reasoning_summary: str,
    reasoning_confidence: float,
    report_excerpt: str
):
    """获取 Uncertainty Handling 节点的 Prompts"""
    return {
        "system": UNCERTAINTY_EXPERT_SYSTEM,
        "user": UNCERTAINTY_PROMPT.format(
            topic=escape_template_braces(topic),
            findings_summary=escape_template_braces(findings_summary),
            reasoning_summary=escape_template_braces(reasoning_summary),
            reasoning_confidence=reasoning_confidence,
            report_excerpt=escape_template_braces(report_excerpt)
        )
    }

def get_reflection_prompts(
    topic: str,
    reasoning_summary: str,
    findings_count: int
):
    """获取 Reflection 节点的 Prompts"""
    return {
        "system": REFLECTION_EXPERT_SYSTEM,
        "user": REFLECTION_PROMPT.format(
            topic=escape_template_braces(topic),
            reasoning_summary=escape_template_braces(reasoning_summary),
            findings_count=findings_count
        )
    }

def get_analyst_step_prompts(
    focus: str,
    evidence_text: str,
    step_name: str
):
    """获取 Analyst 推理步骤的 Prompts"""
    return {
        "system": TOP_ANALYST_SYSTEM.format(
            focus=escape_template_braces(focus),
            evidence_text=escape_template_braces(evidence_text)
        ),
        "user": ANALYST_STEP_PROMPT.format(step_name=escape_template_braces(step_name))
    }

def get_report_generation_prompts(
    topic: str,
    reasoning_summary: str,
    evidence_text: str
):
    """获取报告生成的 Prompts"""
    return {
        "system": REPORT_SYNTHESIZER_SYSTEM,
        "user": REPORT_GENERATION_PROMPT.format(
            topic=escape_template_braces(topic),
            reasoning_summary=escape_template_braces(reasoning_summary),
            evidence_text=escape_template_braces(evidence_text)
        )
    }

# ============================================================================
# Prompt Configuration (Prompt 配置)
# ============================================================================

# 默认温度设置
DEFAULT_TEMPERATURES = {
    "planner": 0.7,
    "executor": 0.0,
    "progress_check": 0.3,
    "validation": 0.3,
    "uncertainty": 0.3,
    "reflection": 0.3,
    "analyst": 0.4,
}

# 默认模型选择
DEFAULT_MODELS = {
    "planner": "moonshot-v1-32k",
    "executor": "moonshot-v1-32k",
    "progress_check": "moonshot-v1-32k",
    "validation": "moonshot-v1-32k",
    "uncertainty": "moonshot-v1-32k",
    "reflection": "moonshot-v1-32k",
    "analyst": "moonshot-v1-32k",
}

def get_node_config(node_name: str) -> dict:
    """获取节点的配置（温度和模型）"""
    return {
        "temperature": DEFAULT_TEMPERATURES.get(node_name, 0.3),
        "model": DEFAULT_MODELS.get(node_name, "moonshot-v1-32k")
    }
