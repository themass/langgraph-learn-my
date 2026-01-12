#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ReAct (Reasoning + Acting) 生产级实现
=====================================

基于 ReAct 推理范式构建的生产级智能代理系统，包含：
1. 任务分析 - 理解任务需求和复杂度
2. 知识准备 - 主动获取领域相关知识
3. Think-Act-Observe 循环 - 核心推理与行动循环
4. 反思机制 - 评估策略有效性并调整
5. 答案生成 - 生成可靠的解决方案
6. 质量评估 - 评估答案质量并决定是否重试

特点：
- 保持 ReAct 核心思想：Think-Act-Observe 循环
- 增强生产级功能：知识管理、策略规划、反思机制
- 代码风格统一：使用统一的日志、Prompt 配置
- 工具集成完善：多种工具支持，错误处理健全
"""

from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from utils import get_llm
from log_utils import log_node_input, log_node_output, log_prompt
from rag import BasicRAG, AgenticRAG
from prompts.react_production_prompts import (
    REACT_PRODUCTION_SYSTEM_PROMPT,
    format_task_analysis_prompt,
    format_knowledge_prep_prompt,
    format_think_prompt,
    format_observe_reflect_prompt,
    format_answer_generation_prompt,
    format_quality_assessment_prompt
)
import json
import re
from datetime import datetime


# =================================================================
# 知识库定义
# =================================================================

KNOWLEDGE_BASE = {
    "医学": [
        {"id": "med-001", "topic": "高血压", "content": "高血压是指动脉血压持续升高，收缩压≥140mmHg和/或舒张压≥90mmHg。主要治疗方式包括生活方式改变和药物治疗。"},
        {"id": "med-002", "topic": "糖尿病", "content": "糖尿病是一种代谢紊乱疾病，特征是血糖水平长期升高。包括1型和2型，治疗方式各有不同。"},
        {"id": "med-003", "topic": "感冒", "content": "感冒是由多种病毒引起的上呼吸道感染，通常症状包括鼻塞、流涕、咳嗽和发热。一般为自限性疾病。"},
        {"id": "med-004", "topic": "心脏病", "content": "心脏病包括多种类型，常见症状有胸痛、气短、心悸等。需要根据具体类型进行诊断和治疗。"}
    ],
    "计算机": [
        {"id": "cs-001", "topic": "算法复杂度", "content": "算法复杂度用大O表示法描述算法效率，包括时间复杂度和空间复杂度。常见复杂度有O(1)、O(n)、O(log n)、O(n²)等。"},
        {"id": "cs-002", "topic": "数据结构", "content": "数据结构是数据组织、管理和存储格式，包括数组、链表、树、图等，不同结构适用于不同场景。"},
        {"id": "cs-003", "topic": "网络协议", "content": "网络协议是通信规则的集合，如TCP/IP协议族。TCP提供可靠传输，UDP提供快速但不可靠的传输。"},
        {"id": "cs-004", "topic": "Python", "content": "Python是一种高级编程语言，以简洁易读著称。广泛应用于数据科学、Web开发、自动化等领域。"}
    ],
    "通用": [
        {"id": "gen-001", "topic": "问题解决", "content": "问题解决的一般步骤包括:1.明确问题 2.收集信息 3.分析原因 4.制定方案 5.实施方案 6.评估结果"},
        {"id": "gen-002", "topic": "决策方法", "content": "常见决策方法包括利弊分析法、决策矩阵法、德尔菲法等，适用于不同类型的决策问题。"},
        {"id": "gen-003", "topic": "项目管理", "content": "项目管理包括范围管理、时间管理、成本管理、质量管理等。需要合理规划和控制项目进度。"}
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
    """搜索工具 - 模拟搜索引擎"""
    # 模拟搜索结果
    search_db = {
        "python": "Python是一种高级编程语言，以其简洁的语法和强大的功能而闻名。广泛用于数据科学、Web开发、自动化等领域。",
        "机器学习": "机器学习是人工智能的一个分支，通过算法让计算机从数据中学习模式，无需明确编程。",
        "高血压": "高血压是指动脉血压持续升高的慢性疾病，是心血管疾病的主要危险因素。需要通过生活方式改变和药物治疗来控制。",
        "算法": "算法是解决特定问题的明确步骤序列。算法效率通常用时间复杂度和空间复杂度来衡量。"
    }
    
    query_lower = query.lower()
    for key, value in search_db.items():
        if key in query_lower:
            return f"搜索结果：{value}"
    
    return f"搜索'{query}'未找到直接匹配，建议使用更具体的关键词。"


def calculate_tool(expression: str) -> str:
    """计算工具 - 安全的数学计算"""
    try:
        # 安全检查：只允许数字和基本运算符
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            return "错误：表达式包含不允许的字符"
        
        result = eval(expression)
        return f"计算结果：{result}"
    except Exception as e:
        return f"计算错误：{str(e)}"


def get_time_tool() -> str:
    """获取当前时间工具"""
    return f"当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


def rag_search_tool(query: str, domain: str = "通用") -> str:
    """RAG 检索工具"""
    try:
        knowledge_base = KNOWLEDGE_BASE.get(domain, KNOWLEDGE_BASE["通用"])
        agentic_rag = AgenticRAG(knowledge_base=knowledge_base)
        results = agentic_rag.retrieve(query, max_docs=3)
        
        if results["documents"]:
            docs_text = "\n".join([f"- {doc['content']}" for doc in results["documents"]])
            return f"检索结果：\n{docs_text}"
        else:
            return "未找到相关信息"
    except Exception as e:
        return f"检索错误：{str(e)}"


# 可用工具列表
AVAILABLE_TOOLS = {
    "search": Tool("search", "搜索互联网获取信息", lambda query: search_tool(query)),
    "calculate": Tool("calculate", "执行数学计算", lambda expr: calculate_tool(expr)),
    "get_time": Tool("get_time", "获取当前日期时间", lambda: get_time_tool()),
    "rag_search": Tool("rag_search", "检索领域知识库", lambda query, domain="通用": rag_search_tool(query, domain))
}


# =================================================================
# 状态定义
# =================================================================

class ReActProductionState(TypedDict):
    """ReAct 生产级状态"""
    # 任务相关
    task: str                                      # 原始任务
    domain: str                                    # 任务领域
    task_type: str                                 # 任务类型
    key_entities: List[str]                        # 关键实体
    constraints: List[str]                         # 约束条件
    complexity: str                                # 复杂度
    required_tools: List[str]                      # 所需工具
    
    # 知识相关
    relevant_knowledge: Optional[List[Dict]]       # 相关知识
    knowledge_confidence: Optional[float]          # 知识可信度
    
    # 策略相关
    current_strategy: Optional[str]                # 当前策略
    strategy_effective: Optional[bool]             # 策略是否有效
    
    # ReAct 循环相关
    thought: Optional[str]                         # 当前思考
    action: Optional[str]                          # 当前行动
    action_input: Optional[str]                    # 行动参数
    observation: Optional[str]                     # 观察结果
    reasoning: Optional[str]                       # 推理依据
    
    # 反思相关
    reflection: Optional[str]                      # 反思内容
    action_effective: Optional[bool]               # 行动是否有效
    learned_info: Optional[List[str]]              # 学到的信息
    confidence_score: Optional[float]              # 置信度评分
    
    # 历史记录
    history: List[Dict[str, Any]]                  # 完整历史
    tool_calls: Optional[List[Dict]]               # 工具调用记录
    iteration: int                                 # 当前迭代轮次
    max_iterations: int                            # 最大迭代次数
    
    # 答案相关
    final_answer: str                              # 最终答案
    explanation: Optional[str]                     # 详细解释
    implementation_steps: Optional[List[str]]      # 实施步骤
    alternative_solutions: Optional[List[str]]     # 替代方案
    limitations: Optional[str]                     # 局限性说明
    
    # 质量评估
    quality_score: Optional[float]                 # 质量评分
    completeness_score: Optional[float]            # 完整性
    accuracy_score: Optional[float]                # 准确性
    needs_retry: Optional[bool]                    # 是否需要重试
    
    # 控制标志
    finished: bool                                 # 是否完成
    retry_count: int                               # 重试次数
    tool_success: Optional[bool]                   # 工具执行是否成功


# =================================================================
# 辅助函数
# =================================================================

def parse_json_from_llm(content: str, default: Dict = None) -> Dict:
    """从 LLM 输出中解析 JSON"""
    try:
        # 尝试查找 JSON 块
        json_str = re.search(r'\{.*\}', content, re.DOTALL)
        if json_str:
            return json.loads(json_str.group())
        # 尝试直接解析
        return json.loads(content)
    except:
        return default or {}


def format_knowledge_summary(knowledge: List[Dict]) -> str:
    """格式化知识摘要"""
    if not knowledge:
        return "无相关知识"
    
    summary = []
    for i, item in enumerate(knowledge[:3], 1):  # 最多显示3条
        summary.append(f"{i}. {item.get('topic', '未知主题')}: {item.get('content', '')[:100]}...")
    
    return "\n".join(summary)


def format_history_summary(history: List[Dict], limit: int = 5) -> str:
    """格式化历史摘要"""
    if not history:
        return "无执行历史"
    
    summary = []
    for entry in history[-limit:]:  # 只显示最近N条
        entry_type = entry.get("type", "unknown")
        content = entry.get("content", "")
        
        if len(content) > 100:
            content = content[:100] + "..."
        
        summary.append(f"[{entry_type}] {content}")
    
    return "\n".join(summary)


def format_tools_description() -> str:
    """格式化工具描述"""
    descriptions = []
    for name, tool in AVAILABLE_TOOLS.items():
        descriptions.append(f"- {name}: {tool.description}")
    return "\n".join(descriptions)


# =================================================================
# 节点函数
# =================================================================

def task_analysis_node(state: ReActProductionState) -> Dict[str, Any]:
    """1. 任务分析节点 - 理解任务，提取关键信息"""
    
    log_node_input("task_analysis_node", state)
    
    task = state["task"]
    
    llm = get_llm(temperature=0.3)
    
    human_prompt = format_task_analysis_prompt(task=task)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", REACT_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    log_prompt("task_analysis_node", [
        ("system", REACT_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析结果
    analysis = parse_json_from_llm(result.content, {
        "domain": "通用",
        "task_type": "通用查询",
        "key_entities": [],
        "constraints": [],
        "complexity": "medium",
        "required_tools": ["search"]
    })
    
    # 初始化历史
    history = [{
        "type": "task_analysis",
        "content": f"任务分析完成：领域={analysis['domain']}, 复杂度={analysis['complexity']}"
    }]
    
    output = {
        "domain": analysis.get("domain", "通用"),
        "task_type": analysis.get("task_type", "通用查询"),
        "key_entities": analysis.get("key_entities", []),
        "constraints": analysis.get("constraints", []),
        "complexity": analysis.get("complexity", "medium"),
        "required_tools": analysis.get("required_tools", ["search"]),
        "history": history,
        "iteration": 0,
        "max_iterations": 10,  # 最多10轮迭代
        "retry_count": 0
    }
    
    log_node_output("task_analysis_node", output)
    
    return output


def knowledge_preparation_node(state: ReActProductionState) -> Dict[str, Any]:
    """2. 知识准备节点 - 检索领域相关知识"""
    
    log_node_input("knowledge_preparation_node", state)
    
    task = state["task"]
    domain = state.get("domain", "通用")
    key_entities = state.get("key_entities", [])
    
    # 使用 RAG 检索知识
    knowledge_base = KNOWLEDGE_BASE.get(domain, KNOWLEDGE_BASE["通用"])
    agentic_rag = AgenticRAG(knowledge_base=knowledge_base)
    
    # 构建检索查询
    search_query = task
    if key_entities:
        search_query = f"{task} {' '.join(key_entities[:3])}"
    
    rag_results = agentic_rag.retrieve(search_query, max_docs=5)
    relevant_knowledge = rag_results.get("documents", [])
    
    # 评估知识充分性
    llm = get_llm(temperature=0.3)
    
    human_prompt = format_knowledge_prep_prompt(
        task=task,
        domain=domain,
        key_entities=", ".join(key_entities) if key_entities else "无",
        retrieved_knowledge=format_knowledge_summary(relevant_knowledge)
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", REACT_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    log_prompt("knowledge_preparation_node", [
        ("system", REACT_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析评估结果
    assessment = parse_json_from_llm(result.content, {
        "knowledge_sufficient": True,
        "knowledge_confidence": 0.7
    })
    
    # 更新历史
    history = state.get("history", [])
    history.append({
        "type": "knowledge_preparation",
        "content": f"检索到 {len(relevant_knowledge)} 条相关知识，置信度: {assessment.get('knowledge_confidence', 0.7)}"
    })
    
    output = {
        "relevant_knowledge": relevant_knowledge,
        "knowledge_confidence": assessment.get("knowledge_confidence", 0.7),
        "history": history,
        "observation": "知识准备完成，已检索相关领域知识",
        "current_strategy": "基于知识的 Think-Act-Observe 循环"
    }
    
    log_node_output("knowledge_preparation_node", output)
    
    return output


def think_node(state: ReActProductionState) -> Dict[str, Any]:
    """3. 思考节点 - ReAct 核心：分析情况，决定行动"""
    
    log_node_input("think_node", state)
    
    task = state["task"]
    iteration = state.get("iteration", 0) + 1  # 增加迭代计数
    max_iterations = state.get("max_iterations", 10)
    observation = state.get("observation", "任务刚开始")
    relevant_knowledge = state.get("relevant_knowledge", [])
    history = state.get("history", [])
    current_strategy = state.get("current_strategy", "Think-Act-Observe 循环")
    
    llm = get_llm(temperature=0.3)
    
    human_prompt = format_think_prompt(
        task=task,
        iteration=iteration,
        max_iterations=max_iterations,
        observation=observation,
        knowledge_summary=format_knowledge_summary(relevant_knowledge),
        history_summary=format_history_summary(history),
        tools_description=format_tools_description(),
        current_strategy=current_strategy
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", REACT_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    log_prompt("think_node", [
        ("system", REACT_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析思考结果
    decision = parse_json_from_llm(result.content, {
        "thought": "继续分析问题",
        "action": "search",
        "action_input": task,
        "reasoning": "需要更多信息",
        "confidence": 0.5
    })
    
    # 更新历史
    history.append({
        "type": "thought",
        "content": decision.get("thought", ""),
        "iteration": iteration
    })
    
    output = {
        "thought": decision.get("thought", ""),
        "action": decision.get("action", "search"),
        "action_input": str(decision.get("action_input", "")),
        "reasoning": decision.get("reasoning", ""),
        "confidence_score": decision.get("confidence", 0.5),
        "history": history,
        "iteration": iteration
    }
    
    log_node_output("think_node", output)
    
    return output


def act_node(state: ReActProductionState) -> Dict[str, Any]:
    """4. 行动节点 - 执行选定的工具"""
    
    log_node_input("act_node", state)
    
    action = state.get("action", "finish")
    action_input = state.get("action_input", "")
    domain = state.get("domain", "通用")
    
    tool_success = True
    observation = ""
    
    if action == "finish":
        observation = "准备生成最终答案"
    else:
        # 执行工具
        try:
            if action in AVAILABLE_TOOLS:
                tool = AVAILABLE_TOOLS[action]
                
                # 根据工具类型传递参数
                if action == "search":
                    observation = tool.execute(query=action_input)
                elif action == "calculate":
                    observation = tool.execute(expr=action_input)
                elif action == "get_time":
                    observation = tool.execute()
                elif action == "rag_search":
                    observation = tool.execute(query=action_input, domain=domain)
                else:
                    observation = tool.execute()
                    
                tool_success = True
            else:
                observation = f"错误：工具 '{action}' 不存在"
                tool_success = False
                
        except Exception as e:
            observation = f"工具执行失败：{str(e)}"
            tool_success = False
    
    # 记录工具调用
    tool_calls = state.get("tool_calls", [])
    if action != "finish":
        tool_calls.append({
            "tool": action,
            "input": action_input,
            "output": observation,
            "success": tool_success,
            "timestamp": datetime.now().isoformat()
        })
    
    # 更新历史
    history = state.get("history", [])
    history.append({
        "type": "action",
        "content": f"行动: {action}({action_input})"
    })
    history.append({
        "type": "observation",
        "content": observation
    })
    
    output = {
        "observation": observation,
        "tool_success": tool_success,
        "tool_calls": tool_calls,
        "history": history
    }
    
    log_node_output("act_node", output)
    
    return output


def observe_reflect_node(state: ReActProductionState) -> Dict[str, Any]:
    """5. 观察与反思节点 - 评估行动效果，调整策略"""
    
    log_node_input("observe_reflect_node", state)
    
    action = state.get("action", "")
    action_input = state.get("action_input", "")
    observation = state.get("observation", "")
    tool_success = state.get("tool_success", True)
    current_strategy = state.get("current_strategy", "Think-Act-Observe 循环")
    history = state.get("history", [])
    
    llm = get_llm(temperature=0.3)
    
    human_prompt = format_observe_reflect_prompt(
        action=action,
        action_input=action_input,
        observation=observation,
        tool_success=tool_success,
        current_strategy=current_strategy,
        history_summary=format_history_summary(history)
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", REACT_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    log_prompt("observe_reflect_node", [
        ("system", REACT_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析反思结果
    reflection_data = parse_json_from_llm(result.content, {
        "reflection": "行动已执行",
        "action_effective": True,
        "learned_info": [],
        "strategy_effective": True,
        "confidence_score": 0.7,
        "should_continue": True
    })
    
    # 更新历史
    history.append({
        "type": "reflection",
        "content": reflection_data.get("reflection", "")
    })
    
    # 如果策略需要调整
    new_strategy = current_strategy
    if not reflection_data.get("strategy_effective", True):
        new_strategy = reflection_data.get("suggested_strategy", current_strategy)
    
    output = {
        "reflection": reflection_data.get("reflection", ""),
        "action_effective": reflection_data.get("action_effective", True),
        "learned_info": reflection_data.get("learned_info", []),
        "strategy_effective": reflection_data.get("strategy_effective", True),
        "current_strategy": new_strategy,
        "confidence_score": reflection_data.get("confidence_score", 0.7),
        "should_continue": reflection_data.get("should_continue", True),
        "history": history
    }
    
    log_node_output("observe_reflect_node", output)
    
    return output


def answer_generation_node(state: ReActProductionState) -> Dict[str, Any]:
    """6. 答案生成节点 - 生成最终答案"""
    
    log_node_input("answer_generation_node", state)
    
    task = state["task"]
    history = state.get("history", [])
    relevant_knowledge = state.get("relevant_knowledge", [])
    tool_calls = state.get("tool_calls", [])
    
    llm = get_llm(temperature=0.3)
    
    # 格式化工具调用摘要
    tool_calls_summary = "无工具调用"
    if tool_calls:
        tool_summary = []
        for tc in tool_calls:
            tool_summary.append(f"- {tc['tool']}: {tc['output'][:100]}...")
        tool_calls_summary = "\n".join(tool_summary)
    
    human_prompt = format_answer_generation_prompt(
        task=task,
        complete_history=format_history_summary(history, limit=20),
        knowledge_summary=format_knowledge_summary(relevant_knowledge),
        tool_calls_summary=tool_calls_summary
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", REACT_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    log_prompt("answer_generation_node", [
        ("system", REACT_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析答案
    answer_data = parse_json_from_llm(result.content, {
        "final_answer": result.content,
        "explanation": "",
        "confidence": 0.8
    })
    
    output = {
        "final_answer": answer_data.get("final_answer", result.content),
        "explanation": answer_data.get("explanation", ""),
        "implementation_steps": answer_data.get("implementation_steps", []),
        "alternative_solutions": answer_data.get("alternative_solutions", []),
        "limitations": answer_data.get("limitations", ""),
        "confidence_score": answer_data.get("confidence", 0.8),
        "finished": True
    }
    
    log_node_output("answer_generation_node", output)
    
    return output


def quality_assessment_node(state: ReActProductionState) -> Dict[str, Any]:
    """7. 质量评估节点 - 评估答案质量"""
    
    log_node_input("quality_assessment_node", state)
    
    task = state["task"]
    final_answer = state.get("final_answer", "")
    explanation = state.get("explanation", "")
    history = state.get("history", [])
    confidence = state.get("confidence_score", 0.8)
    
    llm = get_llm(temperature=0.2)  # 降低温度以获得更稳定的评估
    
    human_prompt = format_quality_assessment_prompt(
        task=task,
        final_answer=final_answer,
        explanation=explanation,
        history_summary=format_history_summary(history, limit=10),
        confidence=confidence
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", REACT_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    log_prompt("quality_assessment_node", [
        ("system", REACT_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析评估结果
    assessment = parse_json_from_llm(result.content, {
        "quality_score": 7.0,
        "completeness_score": 7.0,
        "accuracy_score": 7.0,
        "needs_retry": False
    })
    
    output = {
        "quality_score": assessment.get("quality_score", 7.0),
        "completeness_score": assessment.get("completeness_score", 7.0),
        "accuracy_score": assessment.get("accuracy_score", 7.0),
        "clarity_score": assessment.get("clarity_score", 7.0),
        "needs_retry": assessment.get("needs_retry", False)
    }
    
    log_node_output("quality_assessment_node", output)
    
    return output


# =================================================================
# 条件边函数
# =================================================================

def should_continue_thinking(state: ReActProductionState) -> str:
    """判断是否继续 Think-Act-Observe 循环"""
    action = state.get("action", "finish")
    
    # 如果明确选择 finish
    if action == "finish":
        return "answer_generation"
    
    # 检查是否达到最大迭代次数
    iteration = state.get("iteration", 0)
    max_iterations = state.get("max_iterations", 10)
    
    if iteration >= max_iterations:
        return "answer_generation"
    
    # 检查置信度是否足够高
    confidence_score = state.get("confidence_score", 0.0)
    if confidence_score >= 0.95:  # 非常高的置信度
        return "answer_generation"
    
    # 检查反思结果
    should_continue = state.get("should_continue", True)
    if not should_continue:
        return "answer_generation"
    
    # 继续循环
    return "think"


def should_retry(state: ReActProductionState) -> str:
    """判断是否需要重试"""
    needs_retry = state.get("needs_retry", False)
    retry_count = state.get("retry_count", 0)
    quality_score = state.get("quality_score", 7.0)
    
    # 如果质量分数低于6且重试次数少于2次
    if (needs_retry or quality_score < 6.0) and retry_count < 2:
        return "knowledge_preparation"  # 返回知识准备节点重新开始
    
    # 接受当前答案
    return END


# =================================================================
# 图构建
# =================================================================

def create_react_production_graph():
    """创建 ReAct 生产级工作流图"""
    
    graph = StateGraph(ReActProductionState)
    
    # 添加节点
    # 1. 任务分析节点：分析任务领域、类型、复杂度，确定所需工具
    graph.add_node("task_analysis", task_analysis_node)
    
    # 2. 知识准备节点：使用RAG检索领域知识，评估知识充分性
    graph.add_node("knowledge_preparation", knowledge_preparation_node)
    
    # 3. 思考节点：分析当前状态，决定下一步行动（Think）
    graph.add_node("think", think_node)
    
    # 4. 行动节点：执行工具调用，获取外部信息（Act）
    graph.add_node("act", act_node)
    
    # 5. 观察与反思节点：评估行动效果，调整策略（Observe + Reflect）
    graph.add_node("observe_reflect", observe_reflect_node)
    
    # 6. 答案生成节点：基于完整历史生成最终答案
    graph.add_node("answer_generation", answer_generation_node)
    
    # 7. 质量评估节点：评估答案质量，决定是否重试
    graph.add_node("quality_assessment", quality_assessment_node)
    
    # 设置入口点
    graph.set_entry_point("task_analysis")
    
    # 添加边
    graph.add_edge("task_analysis", "knowledge_preparation")
    graph.add_edge("knowledge_preparation", "think")
    
    # Think-Act-Observe 循环
    graph.add_edge("think", "act")
    graph.add_edge("act", "observe_reflect")
    
    # 条件边：决定是否继续循环
    graph.add_conditional_edges(
        "observe_reflect",
        should_continue_thinking,
        {
            "think": "think",                      # 继续循环
            "answer_generation": "answer_generation"  # 生成答案
        }
    )
    
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

def demo_react_production():
    """ReAct 生产级 Demo"""
    
    print("=" * 60)
    print("ReAct (Reasoning + Acting) 生产级实现 Demo")
    print("=" * 60)
    
    # 测试问题
    test_questions = [
        "Python 的时间复杂度 O(n) 是什么意思？它与 O(n²) 有什么区别？",
        "如果今天要进行一个重要会议，现在是什么时间？我应该准备什么？",
        "计算 (15 + 27) * 3 - 8 的结果，并解释计算步骤"
    ]
    
    graph = create_react_production_graph()
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*60}")
        print(f"【问题 {i}】")
        print(f"问题：{question}\n")
        
        initial_state = {
            "task": question,
            "history": [],
            "finished": False
        }
        
        result = graph.invoke(initial_state)
        
        # 显示结果
        print("\n" + "="*60)
        print("【执行结果】")
        print(f"\n任务领域：{result.get('domain', 'N/A')}")
        print(f"任务复杂度：{result.get('complexity', 'N/A')}")
        print(f"执行轮次：{result.get('iteration', 0)} 轮")
        
        print(f"\n【最终答案】")
        print(result.get('final_answer', '未生成答案'))
        
        if result.get('explanation'):
            print(f"\n【详细解释】")
            print(result.get('explanation'))
        
        if result.get('implementation_steps'):
            print(f"\n【实施步骤】")
            for step_idx, step in enumerate(result.get('implementation_steps', []), 1):
                print(f"{step_idx}. {step}")
        
        if result.get('alternative_solutions'):
            print(f"\n【替代方案】")
            for alt_idx, alt in enumerate(result.get('alternative_solutions', []), 1):
                print(f"{alt_idx}. {alt}")
        
        if result.get('limitations'):
            print(f"\n【局限性说明】")
            print(result.get('limitations'))
        
        # 质量评估
        quality_score = result.get('quality_score', 0)
        print(f"\n【质量评估】")
        print(f"总体质量：{quality_score}/10")
        print(f"完整性：{result.get('completeness_score', 0)}/10")
        print(f"准确性：{result.get('accuracy_score', 0)}/10")
        print(f"置信度：{result.get('confidence_score', 0):.2f}")
        
        # 工具调用统计
        tool_calls = result.get('tool_calls', [])
        if tool_calls:
            print(f"\n【工具调用统计】")
            print(f"总计调用：{len(tool_calls)} 次")
            for tc in tool_calls:
                status = "✓" if tc.get('success') else "✗"
                print(f"  {status} {tc['tool']}: {tc['output'][:50]}...")
        
        print("=" * 60)


if __name__ == "__main__":
    demo_react_production()
