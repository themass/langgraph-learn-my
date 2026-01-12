#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Plan-and-Execute (规划与执行) 范式
===================================

核心思想：先制定完整计划，然后依次执行，相比 ReAct 减少了每步的思考成本。

特点：
- Plan（规划）：一次性将任务分解为步骤序列
- Execute（执行）：依次执行每个步骤
- Progress Check（检查）：评估完成情况
- Re-plan（重规划）：必要时调整计划
- 适用于目标明确、可分解的任务
"""

from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from utils import get_llm
from log_utils import log_node_input, log_node_output, log_prompt
from prompts.plan_execute_prompts import (
    PLAN_EXECUTE_SYSTEM_PROMPT,
    format_plan_prompt,
    format_execute_prompt,
    format_progress_check_prompt,
    format_finish_prompt
)
import json
import re


# =================================================================
# 工具定义
# =================================================================

class Tool:
    """简单工具定义"""
    def __init__(self, name: str, description: str, func: callable):
        self.name = name
        self.description = description
        self.func = func
    
    def execute(self, **kwargs):
        return self.func(**kwargs)


def search_tool(query: str) -> str:
    """搜索工具"""
    results = {
        "Python": "Python是一种高级编程语言，广泛用于数据科学、Web开发、自动化等。",
        "机器学习": "机器学习是AI的一个分支，让计算机从数据中学习模式。",
        "项目管理": "项目管理包括规划、执行、监控和收尾四个阶段。",
        "团队协作": "有效的团队协作需要清晰的沟通、明确的角色分工和共同的目标。"
    }
    
    for key, value in results.items():
        if key.lower() in query.lower():
            return f"搜索结果：{value}"
    
    return f"搜索'{query}'：未找到直接匹配的结果。"


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
    return f"分析结果：已完成对数据的分析 - {data[:100]}..."


# 可用工具列表
AVAILABLE_TOOLS = {
    "search": Tool("search", "搜索信息", lambda q: search_tool(q)),
    "calculate": Tool("calculate", "数学计算", lambda e: calculate_tool(e)),
    "analyze": Tool("analyze", "数据分析", lambda d: analyze_tool(d))
}


# =================================================================
# 状态定义
# =================================================================

class PlanExecuteState(TypedDict):
    """Plan-and-Execute 状态"""
    task: str  # 原始任务
    plan: Optional[List[Dict[str, Any]]]  # 计划步骤列表
    current_step_index: int  # 当前步骤索引
    step_results: List[Dict[str, Any]]  # 步骤执行结果
    needs_replan: bool  # 是否需要重新规划
    final_answer: Optional[str]  # 最终答案
    finished: bool  # 是否完成


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


def format_plan_summary(plan: List[Dict]) -> str:
    """格式化计划摘要"""
    if not plan:
        return "无计划"
    
    summary = []
    for step in plan:
        summary.append(f"步骤{step['step_id']}: {step['description']} (类型: {step.get('action_type', 'N/A')})")
    return "\n".join(summary)


def format_results_summary(results: List[Dict]) -> str:
    """格式化结果摘要"""
    if not results:
        return "无执行结果"
    
    summary = []
    for result in results:
        step_id = result.get('step_id', '?')
        success = "✓" if result.get('success', False) else "✗"
        summary.append(f"{success} 步骤{step_id}: {result.get('result', 'N/A')[:80]}...")
    return "\n".join(summary)


# =================================================================
# 节点函数
# =================================================================

def plan_node(state: PlanExecuteState) -> Dict[str, Any]:
    """规划节点 - 将任务分解为步骤序列"""
    
    log_node_input("plan_node", state)
    
    task = state["task"]
    
    llm = get_llm(temperature=0.3)
    
    human_prompt = format_plan_prompt(task=task)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", PLAN_EXECUTE_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    log_prompt("plan_node", [
        ("system", PLAN_EXECUTE_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析计划
    plan_data = parse_json_from_llm(result.content, {
        "plan": [
            {"step_id": 1, "description": "分析任务", "action_type": "analyze"},
            {"step_id": 2, "description": "执行主要步骤", "action_type": "search"},
            {"step_id": 3, "description": "总结结果", "action_type": "synthesize"}
        ]
    })
    
    plan = plan_data.get("plan", [])
    
    output = {
        "plan": plan,
        "current_step_index": 0,
        "step_results": [],
        "needs_replan": False
    }
    
    log_node_output("plan_node", output)
    
    return output


def execute_step_node(state: PlanExecuteState) -> Dict[str, Any]:
    """执行步骤节点 - 执行当前步骤"""
    
    log_node_input("execute_step_node", state)
    
    plan = state.get("plan", [])
    current_index = state.get("current_step_index", 0)
    step_results = state.get("step_results", [])
    
    if current_index >= len(plan):
        return {"finished": True}
    
    current_step = plan[current_index]
    
    llm = get_llm(temperature=0.3)
    
    human_prompt = format_execute_prompt(
        step_id=current_step["step_id"],
        description=current_step["description"],
        action_type=current_step.get("action_type", "general"),
        context="",
        previous_results=format_results_summary(step_results),
        available_tools=format_tools_description()
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", PLAN_EXECUTE_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    log_prompt("execute_step_node", [
        ("system", PLAN_EXECUTE_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析执行结果
    exec_data = parse_json_from_llm(result.content, {
        "result": result.content,
        "success": True,
        "needs_replan": False
    })
    
    # 尝试执行工具（如果需要）
    action_type = current_step.get("action_type", "")
    if action_type in AVAILABLE_TOOLS and not exec_data.get("result"):
        try:
            tool = AVAILABLE_TOOLS[action_type]
            tool_result = tool.execute(q=current_step["description"])
            exec_data["result"] = tool_result
        except:
            pass
    
    # 记录结果
    step_result = {
        "step_id": current_step["step_id"],
        "description": current_step["description"],
        "result": exec_data.get("result", ""),
        "success": exec_data.get("success", True),
        "observations": exec_data.get("observations", "")
    }
    
    step_results.append(step_result)
    
    output = {
        "step_results": step_results,
        "current_step_index": current_index + 1,
        "needs_replan": exec_data.get("needs_replan", False)
    }
    
    log_node_output("execute_step_node", output)
    
    return output


def check_progress_node(state: PlanExecuteState) -> Dict[str, Any]:
    """检查进度节点 - 评估任务完成情况"""
    
    log_node_input("check_progress_node", state)
    
    task = state["task"]
    plan = state.get("plan", [])
    step_results = state.get("step_results", [])
    current_index = state.get("current_step_index", 0)
    
    llm = get_llm(temperature=0.3)
    
    human_prompt = format_progress_check_prompt(
        task=task,
        plan=format_plan_summary(plan),
        completed_steps=format_results_summary(step_results),
        current_step_id=current_index + 1
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", PLAN_EXECUTE_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    log_prompt("check_progress_node", [
        ("system", PLAN_EXECUTE_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析进度评估
    progress_data = parse_json_from_llm(result.content, {
        "completion_percentage": 50,
        "on_track": True,
        "needs_replan": False
    })
    
    output = {
        "needs_replan": progress_data.get("needs_replan", False)
    }
    
    log_node_output("check_progress_node", output)
    
    return output


def finish_node(state: PlanExecuteState) -> Dict[str, Any]:
    """完成节点 - 生成最终答案"""
    
    log_node_input("finish_node", state)
    
    task = state["task"]
    plan = state.get("plan", [])
    step_results = state.get("step_results", [])
    
    llm = get_llm(temperature=0.3)
    
    human_prompt = format_finish_prompt(
        task=task,
        plan=format_plan_summary(plan),
        all_results=format_results_summary(step_results)
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", PLAN_EXECUTE_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    log_prompt("finish_node", [
        ("system", PLAN_EXECUTE_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析最终答案
    finish_data = parse_json_from_llm(result.content, {
        "final_answer": result.content
    })
    
    output = {
        "final_answer": finish_data.get("final_answer", result.content),
        "finished": True
    }
    
    log_node_output("finish_node", output)
    
    return output


# =================================================================
# 条件边函数
# =================================================================

def should_continue_execution(state: PlanExecuteState) -> str:
    """判断是否继续执行"""
    plan = state.get("plan", [])
    current_index = state.get("current_step_index", 0)
    needs_replan = state.get("needs_replan", False)
    
    # 如果需要重新规划（基础版不实现）
    if needs_replan:
        return "finish"  # 简化：直接完成
    
    # 如果还有步骤未执行
    if current_index < len(plan):
        return "execute"
    
    # 所有步骤已完成
    return "finish"


# =================================================================
# 构建图
# =================================================================

def create_plan_execute_graph():
    """创建 Plan-and-Execute 图"""
    
    graph = StateGraph(PlanExecuteState)
    
    # 添加节点
    graph.add_node("plan", plan_node)
    graph.add_node("execute", execute_step_node)
    graph.add_node("check_progress", check_progress_node)
    graph.add_node("finish", finish_node)
    
    # 设置入口点
    graph.set_entry_point("plan")
    
    # 添加边
    graph.add_edge("plan", "execute")
    graph.add_edge("execute", "check_progress")
    
    # 条件边：决定是否继续执行
    graph.add_conditional_edges(
        "check_progress",
        should_continue_execution,
        {
            "execute": "execute",  # 继续执行下一步
            "finish": "finish"     # 完成
        }
    )
    
    graph.add_edge("finish", END)
    
    return graph.compile()


# =================================================================
# Demo 示例
# =================================================================

def demo_plan_execute():
    """Plan-and-Execute Demo"""
    
    print("=" * 60)
    print("Plan-and-Execute (规划与执行) Demo")
    print("=" * 60)
    
    # 测试问题
    test_questions = [
        "如何提高团队的工作效率？请给出具体可行的步骤。",
        "设计一个用户友好的登录系统需要哪些步骤？"
    ]
    
    graph = create_plan_execute_graph()
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*60}")
        print(f"【问题 {i}】")
        print(f"问题：{question}\n")
        
        initial_state = {
            "task": question,
            "plan": None,
            "current_step_index": 0,
            "step_results": [],
            "needs_replan": False,
            "final_answer": None,
            "finished": False
        }
        
        result = graph.invoke(initial_state)
        
        # 显示结果
        print("\n【执行计划】")
        for step in result.get("plan", []):
            print(f"{step['step_id']}. {step['description']} ({step.get('action_type', 'N/A')})")
        
        print("\n【执行结果】")
        for step_result in result.get("step_results", []):
            status = "✓" if step_result.get("success") else "✗"
            print(f"{status} 步骤{step_result['step_id']}: {step_result['description']}")
            print(f"   结果: {step_result['result'][:100]}...")
        
        print(f"\n【最终答案】")
        print(result.get("final_answer", "未生成答案"))
        print("=" * 60)


if __name__ == "__main__":
    demo_plan_execute()
