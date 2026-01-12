#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Plan-and-Execute (规划与执行) 生产级实现
========================================

基于 Plan-and-Execute 策略构建的生产级智能代理系统，包含：
1. 任务分析 - 深入理解任务需求和复杂度
2. 知识准备 - 主动获取领域相关知识
3. 详细规划 - 制定包含风险评估的执行计划
4. 步骤执行 - 基于知识的高质量执行
5. 进度评估 - 实时监控和质量保证
6. 重新规划 - 遇到问题时灵活调整
7. 答案生成 - 生成可靠的解决方案
8. 质量评估 - 评估整体质量并决定是否重试

特点：
- 保持 Plan-and-Execute 核心思想：先规划后执行
- 增强生产级功能：知识增强、风险评估、质量保证
- 代码风格统一：使用统一的日志、Prompt 配置
- 灵活性强：支持重新规划和策略调整
"""

from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from utils import get_llm
from log_utils import log_node_input, log_node_output, log_prompt
from rag import AgenticRAG
from prompts.plan_execute_production_prompts import (
    PLAN_EXECUTE_PRODUCTION_SYSTEM_PROMPT,
    format_task_analysis_prompt,
    format_detailed_plan_prompt,
    format_replan_prompt,
    format_execute_with_knowledge_prompt,
    format_progress_assessment_prompt,
    format_quality_assessment_prompt,
    format_final_answer_prompt
)
import json
import re
from datetime import datetime


# =================================================================
# 知识库定义
# =================================================================

KNOWLEDGE_BASE = {
    "项目管理": [
        {"id": "pm-001", "topic": "敏捷开发", "content": "敏捷开发强调迭代、快速反馈和持续改进，适合需求变化频繁的项目。"},
        {"id": "pm-002", "topic": "风险管理", "content": "项目风险管理包括识别、评估、应对和监控四个步骤。"},
        {"id": "pm-003", "topic": "团队协作", "content": "有效的团队协作需要清晰的沟通、明确的角色和共同的目标。"}
    ],
    "计算机": [
        {"id": "cs-001", "topic": "系统设计", "content": "系统设计需要考虑可扩展性、可靠性、性能和安全性四个关键维度。"},
        {"id": "cs-002", "topic": "数据库", "content": "选择数据库时需要考虑数据模型、性能需求、一致性要求和运维成本。"},
        {"id": "cs-003", "topic": "API设计", "content": "好的API设计应该是直观的、一致的、文档完善的和版本化的。"}
    ],
    "通用": [
        {"id": "gen-001", "topic": "问题解决", "content": "问题解决的一般步骤：明确问题、收集信息、分析原因、制定方案、实施和评估。"},
        {"id": "gen-002", "topic": "决策方法", "content": "常见决策方法包括利弊分析、决策矩阵、德尔菲法等。"},
        {"id": "gen-003", "topic": "沟通技巧", "content": "有效沟通包括清晰表达、积极倾听、及时反馈和换位思考。"}
    ]
}


# =================================================================
# 工具定义
# =================================================================

class Tool:
    """工具定义"""
    def __init__(self, name: str, description: str, func: callable):
        self.name = name
        self.description = description
        self.func = func
    
    def execute(self, **kwargs):
        return self.func(**kwargs)


def search_tool(query: str) -> str:
    """搜索工具"""
    search_db = {
        "项目管理": "项目管理是规划、组织、领导和控制项目活动，以实现特定目标的过程。",
        "敏捷开发": "敏捷开发是一种迭代式的软件开发方法，强调快速交付、持续改进和团队协作。",
        "系统设计": "系统设计是软件工程中将需求转化为可实现架构的过程，需要考虑性能、可扩展性等因素。",
        "团队效率": "提高团队效率需要：清晰的目标、有效的沟通、合理的流程、适当的工具和良好的文化。"
    }
    
    for key, value in search_db.items():
        if key in query:
            return f"搜索结果：{value}"
    
    return f"搜索'{query}'：未找到直接匹配，建议细化查询。"


def calculate_tool(expression: str) -> str:
    """计算工具"""
    try:
        allowed_chars = set("0123456789+-*/(). ")
        if all(c in allowed_chars for c in expression):
            result = eval(expression)
            return f"计算结果：{result}"
        return "错误：表达式包含不允许的字符"
    except Exception as e:
        return f"计算错误：{str(e)}"


def analyze_tool(data: str) -> str:
    """分析工具"""
    return f"分析完成：已对提供的数据进行深入分析 - {data[:150]}..."


def get_time_tool() -> str:
    """获取时间工具"""
    return f"当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


# 可用工具列表
AVAILABLE_TOOLS = {
    "search": Tool("search", "搜索互联网或知识库", lambda q: search_tool(q)),
    "calculate": Tool("calculate", "执行数学计算", lambda e: calculate_tool(e)),
    "analyze": Tool("analyze", "分析数据或信息", lambda d: analyze_tool(d)),
    "get_time": Tool("get_time", "获取当前时间", lambda: get_time_tool())
}


# =================================================================
# 状态定义
# =================================================================

class PlanExecuteProductionState(TypedDict):
    """Plan-and-Execute 生产级状态"""
    # 任务相关
    task: str                                     # 原始任务
    domain: str                                   # 任务领域
    task_type: str                                # 任务类型
    complexity: str                               # 复杂度
    success_criteria: Optional[str]               # 成功标准
    
    # 知识相关
    relevant_knowledge: Optional[List[Dict]]      # 相关知识
    knowledge_confidence: Optional[float]         # 知识可信度
    
    # 计划相关
    plan: Optional[List[Dict[str, Any]]]          # 执行计划
    critical_path: Optional[List[int]]            # 关键路径
    overall_strategy: Optional[str]               # 整体策略
    estimated_total_time: Optional[str]           # 预估总时间
    
    # 执行相关
    current_step_index: int                       # 当前步骤索引
    step_results: List[Dict[str, Any]]            # 步骤执行结果
    
    # 进度与质量
    completion_percentage: Optional[float]        # 完成百分比
    quality_score: Optional[float]                # 质量评分
    on_track: Optional[bool]                      # 是否按计划进行
    
    # 重规划相关
    needs_replan: bool                            # 是否需要重新规划
    replan_count: int                             # 重规划次数
    replan_reason: Optional[str]                  # 重规划原因
    
    # 工具和历史
    tool_calls: Optional[List[Dict]]              # 工具调用记录
    
    # 答案相关
    final_answer: Optional[str]                   # 最终答案
    explanation: Optional[str]                    # 详细解释
    implementation_steps: Optional[List[str]]     # 实施步骤
    limitations: Optional[str]                    # 局限性说明
    
    # 控制标志
    finished: bool                                # 是否完成
    retry_count: int                              # 重试次数


# =================================================================
# 辅助函数
# =================================================================

def parse_json_from_llm(content: str, default: Dict = None) -> Dict:
    """从 LLM 输出中解析 JSON"""
    try:
        json_str = re.search(r'\{.*\}', content, re.DOTALL)
        if json_str:
            return json.loads(json_str.group())
        return json.loads(content)
    except:
        return default or {}


def format_tools_description() -> str:
    """格式化工具描述"""
    descriptions = []
    for name, tool in AVAILABLE_TOOLS.items():
        descriptions.append(f"- {name}: {tool.description}")
    return "\n".join(descriptions)


def format_knowledge_summary(knowledge: List[Dict]) -> str:
    """格式化知识摘要"""
    if not knowledge:
        return "无相关知识"
    
    summary = []
    for i, item in enumerate(knowledge[:3], 1):
        summary.append(f"{i}. {item.get('topic', '未知')}: {item.get('content', '')[:100]}...")
    return "\n".join(summary)


def format_plan_summary(plan: List[Dict]) -> str:
    """格式化计划摘要"""
    if not plan:
        return "无计划"
    
    summary = []
    for step in plan:
        risk = step.get('risk_level', 'N/A')
        summary.append(
            f"步骤{step['step_id']}: {step['description']} "
            f"(类型: {step.get('action_type', 'N/A')}, 风险: {risk})"
        )
    return "\n".join(summary)


def format_results_summary(results: List[Dict], limit: int = 10) -> str:
    """格式化结果摘要"""
    if not results:
        return "无执行结果"
    
    summary = []
    for result in results[-limit:]:
        step_id = result.get('step_id', '?')
        success = "✓" if result.get('success', False) else "✗"
        quality = result.get('quality_score', 0)
        summary.append(
            f"{success} 步骤{step_id}: {result.get('result', '')[:80]}... "
            f"(质量: {quality}/10)"
        )
    return "\n".join(summary)


# =================================================================
# 节点函数
# =================================================================

def task_analysis_node(state: PlanExecuteProductionState) -> Dict[str, Any]:
    """1. 任务分析节点 - 深入理解任务"""
    
    log_node_input("task_analysis_node", state)
    
    task = state["task"]
    
    llm = get_llm(temperature=0.3)
    
    human_prompt = format_task_analysis_prompt(task=task)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", PLAN_EXECUTE_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    log_prompt("task_analysis_node", [
        ("system", PLAN_EXECUTE_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析任务分析
    analysis = parse_json_from_llm(result.content, {
        "task_type": "通用任务",
        "complexity": "medium",
        "success_criteria": "完成所有必要步骤"
    })
    
    output = {
        "task_type": analysis.get("task_type", "通用任务"),
        "complexity": analysis.get("complexity", "medium"),
        "domain": analysis.get("task_type", "通用"),
        "success_criteria": analysis.get("success_criteria", "完成任务"),
        "replan_count": 0,
        "retry_count": 0
    }
    
    log_node_output("task_analysis_node", output)
    
    return output


def knowledge_preparation_node(state: PlanExecuteProductionState) -> Dict[str, Any]:
    """2. 知识准备节点 - 检索相关知识"""
    
    log_node_input("knowledge_preparation_node", state)
    
    task = state["task"]
    domain = state.get("domain", "通用")
    
    # 使用 RAG 检索知识
    knowledge_base = KNOWLEDGE_BASE.get(domain, KNOWLEDGE_BASE["通用"])
    agentic_rag = AgenticRAG(knowledge_base=knowledge_base)
    
    rag_results = agentic_rag.retrieve(task, max_docs=5)
    relevant_knowledge = rag_results.get("documents", [])
    
    output = {
        "relevant_knowledge": relevant_knowledge,
        "knowledge_confidence": 0.8 if relevant_knowledge else 0.5
    }
    
    log_node_output("knowledge_preparation_node", output)
    
    return output


def detailed_plan_node(state: PlanExecuteProductionState) -> Dict[str, Any]:
    """3. 详细规划节点 - 制定执行计划"""
    
    log_node_input("detailed_plan_node", state)
    
    task = state["task"]
    complexity = state.get("complexity", "medium")
    relevant_knowledge = state.get("relevant_knowledge", [])
    
    llm = get_llm(temperature=0.3)
    
    # 构建任务分析摘要
    task_analysis = f"任务类型: {state.get('task_type', 'N/A')}, 复杂度: {complexity}"
    
    human_prompt = format_detailed_plan_prompt(
        task=task,
        task_analysis=task_analysis,
        available_tools=format_tools_description(),
        knowledge_base=format_knowledge_summary(relevant_knowledge)
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", PLAN_EXECUTE_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    log_prompt("detailed_plan_node", [
        ("system", PLAN_EXECUTE_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析计划
    plan_data = parse_json_from_llm(result.content, {
        "plan": [
            {"step_id": 1, "description": "分析需求", "action_type": "analyze"},
            {"step_id": 2, "description": "制定方案", "action_type": "synthesize"},
            {"step_id": 3, "description": "实施执行", "action_type": "tool_use"}
        ]
    })
    
    plan = plan_data.get("plan", [])
    
    output = {
        "plan": plan,
        "critical_path": plan_data.get("critical_path", []),
        "overall_strategy": plan_data.get("overall_strategy", "按步骤执行"),
        "estimated_total_time": plan_data.get("estimated_total_time", "未知"),
        "current_step_index": 0,
        "step_results": []
    }
    
    log_node_output("detailed_plan_node", output)
    
    return output


def execute_step_node(state: PlanExecuteProductionState) -> Dict[str, Any]:
    """4. 执行步骤节点 - 执行当前步骤"""
    
    log_node_input("execute_step_node", state)
    
    plan = state.get("plan", [])
    current_index = state.get("current_step_index", 0)
    step_results = state.get("step_results", [])
    relevant_knowledge = state.get("relevant_knowledge", [])
    
    if current_index >= len(plan):
        return {"finished": True}
    
    current_step = plan[current_index]
    
    llm = get_llm(temperature=0.3)
    
    # 构建风险警告
    risk_level = current_step.get("risk_level", "low")
    risk_warnings = f"风险等级: {risk_level}"
    if risk_level == "high":
        risk_warnings += "\n注意: 此步骤风险较高，请谨慎执行并做好备选准备。"
    
    human_prompt = format_execute_with_knowledge_prompt(
        step_id=current_step["step_id"],
        description=current_step["description"],
        action_type=current_step.get("action_type", "general"),
        expected_outcome=current_step.get("expected_outcome", "完成当前步骤"),
        task_context=state["task"],
        relevant_knowledge=format_knowledge_summary(relevant_knowledge),
        previous_results=format_results_summary(step_results),
        available_tools=format_tools_description(),
        risk_warnings=risk_warnings
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", PLAN_EXECUTE_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    log_prompt("execute_step_node", [
        ("system", PLAN_EXECUTE_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析执行结果
    exec_data = parse_json_from_llm(result.content, {
        "result": result.content,
        "success": True,
        "quality_score": 7,
        "confidence": 0.7,
        "needs_replan": False
    })
    
    # 尝试执行工具
    action_type = current_step.get("action_type", "")
    tool_used = []
    if action_type in AVAILABLE_TOOLS:
        try:
            tool = AVAILABLE_TOOLS[action_type]
            if action_type == "search":
                tool_result = tool.execute(q=current_step["description"])
            elif action_type == "calculate":
                tool_result = tool.execute(e="1+1")  # 简化示例
            else:
                tool_result = tool.execute(d=current_step["description"])
            
            exec_data["result"] = f"{exec_data.get('result', '')} | 工具输出: {tool_result}"
            tool_used.append(action_type)
        except:
            pass
    
    # 记录工具调用
    tool_calls = state.get("tool_calls", [])
    if tool_used:
        tool_calls.append({
            "step_id": current_step["step_id"],
            "tools": tool_used,
            "timestamp": datetime.now().isoformat()
        })
    
    # 记录步骤结果
    step_result = {
        "step_id": current_step["step_id"],
        "description": current_step["description"],
        "result": exec_data.get("result", ""),
        "success": exec_data.get("success", True),
        "quality_score": exec_data.get("quality_score", 7),
        "confidence": exec_data.get("confidence", 0.7),
        "observations": exec_data.get("observations", ""),
        "tools_used": tool_used
    }
    
    step_results.append(step_result)
    
    output = {
        "step_results": step_results,
        "current_step_index": current_index + 1,
        "tool_calls": tool_calls,
        "needs_replan": exec_data.get("needs_replan", False)
    }
    
    log_node_output("execute_step_node", output)
    
    return output


def progress_assessment_node(state: PlanExecuteProductionState) -> Dict[str, Any]:
    """5. 进度评估节点 - 评估任务进度"""
    
    log_node_input("progress_assessment_node", state)
    
    task = state["task"]
    plan = state.get("plan", [])
    step_results = state.get("step_results", [])
    current_index = state.get("current_step_index", 0)
    success_criteria = state.get("success_criteria", "完成所有步骤")
    
    llm = get_llm(temperature=0.3)
    
    completed_count = len(step_results)
    total_count = len(plan)
    
    human_prompt = format_progress_assessment_prompt(
        task=task,
        full_plan=format_plan_summary(plan),
        completed_count=completed_count,
        total_count=total_count,
        completed_steps=format_results_summary(step_results),
        current_step_id=current_index,
        success_criteria=success_criteria
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", PLAN_EXECUTE_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    log_prompt("progress_assessment_node", [
        ("system", PLAN_EXECUTE_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析进度评估
    progress_data = parse_json_from_llm(result.content, {
        "completion_percentage": 50,
        "quality_score": 7,
        "on_track": True,
        "needs_replan": False
    })
    
    output = {
        "completion_percentage": progress_data.get("completion_percentage", 50),
        "quality_score": progress_data.get("quality_score", 7),
        "on_track": progress_data.get("on_track", True),
        "needs_replan": progress_data.get("needs_replan", False),
        "replan_reason": progress_data.get("replan_reason", "")
    }
    
    log_node_output("progress_assessment_node", output)
    
    return output


def replan_node(state: PlanExecuteProductionState) -> Dict[str, Any]:
    """6. 重新规划节点 - 调整执行计划"""
    
    log_node_input("replan_node", state)
    
    task = state["task"]
    plan = state.get("plan", [])
    step_results = state.get("step_results", [])
    replan_reason = state.get("replan_reason", "需要调整策略")
    replan_count = state.get("replan_count", 0)
    
    if replan_count >= 2:
        # 最多重规划2次
        return {"needs_replan": False}
    
    llm = get_llm(temperature=0.3)
    
    human_prompt = format_replan_prompt(
        task=task,
        original_plan=format_plan_summary(plan),
        completed_steps=format_results_summary(step_results),
        issue=replan_reason,
        failure_analysis="根据执行情况分析"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", PLAN_EXECUTE_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    log_prompt("replan_node", [
        ("system", PLAN_EXECUTE_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析新计划
    replan_data = parse_json_from_llm(result.content, {
        "revised_plan": plan  # 保留原计划
    })
    
    revised_plan = replan_data.get("revised_plan", plan)
    
    output = {
        "plan": revised_plan,
        "needs_replan": False,
        "replan_count": replan_count + 1,
        "current_step_index": len(step_results)  # 从已完成的步骤继续
    }
    
    log_node_output("replan_node", output)
    
    return output


def answer_generation_node(state: PlanExecuteProductionState) -> Dict[str, Any]:
    """7. 答案生成节点 - 生成最终答案"""
    
    log_node_input("answer_generation_node", state)
    
    task = state["task"]
    plan = state.get("plan", [])
    step_results = state.get("step_results", [])
    quality_score = state.get("quality_score", 7)
    
    llm = get_llm(temperature=0.3)
    
    human_prompt = format_final_answer_prompt(
        task=task,
        plan_summary=format_plan_summary(plan),
        execution_results=format_results_summary(step_results),
        quality_assessment=f"整体质量评分: {quality_score}/10"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", PLAN_EXECUTE_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    log_prompt("answer_generation_node", [
        ("system", PLAN_EXECUTE_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析最终答案
    answer_data = parse_json_from_llm(result.content, {
        "final_answer": result.content,
        "confidence": 0.8
    })
    
    output = {
        "final_answer": answer_data.get("final_answer", result.content),
        "explanation": answer_data.get("explanation", ""),
        "implementation_steps": answer_data.get("implementation_steps", []),
        "limitations": answer_data.get("limitations", ""),
        "finished": True
    }
    
    log_node_output("answer_generation_node", output)
    
    return output


def quality_assessment_node(state: PlanExecuteProductionState) -> Dict[str, Any]:
    """8. 质量评估节点 - 评估整体质量"""
    
    log_node_input("quality_assessment_node", state)
    
    task = state["task"]
    plan = state.get("plan", [])
    step_results = state.get("step_results", [])
    final_answer = state.get("final_answer", "")
    success_criteria = state.get("success_criteria", "完成任务")
    
    llm = get_llm(temperature=0.2)
    
    human_prompt = format_quality_assessment_prompt(
        task=task,
        plan=format_plan_summary(plan),
        all_results=format_results_summary(step_results),
        final_output=final_answer[:500],
        success_criteria=success_criteria
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", PLAN_EXECUTE_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    log_prompt("quality_assessment_node", [
        ("system", PLAN_EXECUTE_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析质量评估
    assessment = parse_json_from_llm(result.content, {
        "overall_quality_score": 7.0,
        "meets_criteria": True,
        "needs_refinement": False
    })
    
    output = {
        "quality_score": assessment.get("overall_quality_score", 7.0)
    }
    
    log_node_output("quality_assessment_node", output)
    
    return output


# =================================================================
# 条件边函数
# =================================================================

def should_continue_execution(state: PlanExecuteProductionState) -> str:
    """判断是否继续执行"""
    plan = state.get("plan", [])
    current_index = state.get("current_step_index", 0)
    needs_replan = state.get("needs_replan", False)
    replan_count = state.get("replan_count", 0)
    
    # 如果需要重新规划且还没达到上限
    if needs_replan and replan_count < 2:
        return "replan"
    
    # 如果还有步骤未执行
    if current_index < len(plan):
        return "execute"
    
    # 所有步骤已完成
    return "answer_generation"


def should_retry(state: PlanExecuteProductionState) -> str:
    """判断是否需要重试"""
    quality_score = state.get("quality_score", 7.0)
    retry_count = state.get("retry_count", 0)
    
    # 如果质量评分低于6且重试次数少于1次
    if quality_score < 6.0 and retry_count < 1:
        return "knowledge_preparation"  # 重新开始
    
    # 接受当前结果
    return END


# =================================================================
# 图构建
# =================================================================

def create_plan_execute_production_graph():
    """创建 Plan-and-Execute 生产级工作流图"""
    
    graph = StateGraph(PlanExecuteProductionState)
    
    # 添加节点
    # 1. 任务分析节点：深入理解任务需求、类型和复杂度
    graph.add_node("task_analysis", task_analysis_node)
    
    # 2. 知识准备节点：使用RAG检索相关领域知识
    graph.add_node("knowledge_preparation", knowledge_preparation_node)
    
    # 3. 详细规划节点：制定包含风险评估的执行计划
    graph.add_node("detailed_plan", detailed_plan_node)
    
    # 4. 执行步骤节点：基于知识高质量执行每个步骤
    graph.add_node("execute", execute_step_node)
    
    # 5. 进度评估节点：评估完成进度和质量
    graph.add_node("progress_assessment", progress_assessment_node)
    
    # 6. 重新规划节点：必要时调整执行计划
    graph.add_node("replan", replan_node)
    
    # 7. 答案生成节点：基于执行结果生成最终答案
    graph.add_node("answer_generation", answer_generation_node)
    
    # 8. 质量评估节点：评估整体质量
    graph.add_node("quality_assessment", quality_assessment_node)
    
    # 设置入口点
    graph.set_entry_point("task_analysis")
    
    # 添加边
    graph.add_edge("task_analysis", "knowledge_preparation")
    graph.add_edge("knowledge_preparation", "detailed_plan")
    graph.add_edge("detailed_plan", "execute")
    graph.add_edge("execute", "progress_assessment")
    
    # 条件边：决定是继续执行、重规划还是生成答案
    graph.add_conditional_edges(
        "progress_assessment",
        should_continue_execution,
        {
            "execute": "execute",                      # 继续执行
            "replan": "replan",                        # 重新规划
            "answer_generation": "answer_generation"   # 生成答案
        }
    )
    
    graph.add_edge("replan", "execute")  # 重规划后继续执行
    graph.add_edge("answer_generation", "quality_assessment")
    
    # 条件边：决定是否重试
    graph.add_conditional_edges(
        "quality_assessment",
        should_retry,
        {
            "knowledge_preparation": "knowledge_preparation",  # 重试
            END: END                                           # 结束
        }
    )
    
    return graph.compile()


# =================================================================
# Demo 示例
# =================================================================

def demo_plan_execute_production():
    """Plan-and-Execute 生产级 Demo"""
    
    print("=" * 60)
    print("Plan-and-Execute (规划与执行) 生产级实现 Demo")
    print("=" * 60)
    
    # 测试问题
    test_questions = [
        "如何系统性地提高团队工作效率？请给出完整的实施方案。",
        "设计一个安全可靠的用户登录系统需要考虑哪些关键因素？"
    ]
    
    graph = create_plan_execute_production_graph()
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*60}")
        print(f"【问题 {i}】")
        print(f"问题：{question}\n")
        
        initial_state = {
            "task": question,
            "finished": False
        }
        
        result = graph.invoke(initial_state)
        
        # 显示结果
        print("\n【任务分析】")
        print(f"领域：{result.get('domain', 'N/A')}")
        print(f"复杂度：{result.get('complexity', 'N/A')}")
        print(f"成功标准：{result.get('success_criteria', 'N/A')}")
        
        print("\n【执行计划】")
        for step in result.get("plan", []):
            print(f"{step['step_id']}. {step['description']}")
            print(f"   类型: {step.get('action_type', 'N/A')}, "
                  f"风险: {step.get('risk_level', 'N/A')}")
        
        print(f"\n【执行结果】({len(result.get('step_results', []))} 步）")
        for step_result in result.get("step_results", [])[:5]:  # 显示前5步
            status = "✓" if step_result.get("success") else "✗"
            print(f"{status} 步骤{step_result['step_id']}: {step_result['description']}")
            print(f"   结果: {step_result['result'][:100]}...")
            print(f"   质量: {step_result.get('quality_score', 0)}/10")
        
        print(f"\n【进度信息】")
        print(f"完成度：{result.get('completion_percentage', 0)}%")
        print(f"按计划：{'是' if result.get('on_track') else '否'}")
        print(f"重规划次数：{result.get('replan_count', 0)}")
        
        print(f"\n【最终答案】")
        print(result.get("final_answer", "未生成答案"))
        
        if result.get("explanation"):
            print(f"\n【详细解释】")
            print(result.get("explanation")[:200] + "...")
        
        if result.get("implementation_steps"):
            print(f"\n【实施步骤】")
            for idx, step in enumerate(result.get("implementation_steps", [])[:5], 1):
                print(f"{idx}. {step}")
        
        print(f"\n【质量评估】")
        print(f"整体质量：{result.get('quality_score', 0)}/10")
        
        if result.get("tool_calls"):
            print(f"\n【工具调用】")
            print(f"总计：{len(result.get('tool_calls', []))} 次")
        
        print("=" * 60)


if __name__ == "__main__":
    demo_plan_execute_production()
