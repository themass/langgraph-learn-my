#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Chain-of-Thought (CoT) 生产级实现
==================================

基于 CoT 推理范式构建的生产级专家系统，包含：
1. 知识库检索 - 主动获取领域相关知识
2. 信息收集 - 分析问题需求，确定所需信息
3. 逐步推理 - 基于知识的 CoT 推理过程
4. 不确定性评估 - 评估推理的置信度和可靠性
5. 解决方案生成 - 生成可执行的解决方案

特点：
- 保持 CoT 核心思想：逐步推理、逻辑严密
- 增强生产级功能：知识管理、不确定性处理
- 代码风格统一：使用统一的日志、Prompt 配置
- 单文件实现：所有功能集中在一个脚本中
"""

from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from utils import get_llm
from log_utils import log_node_input, log_node_output, log_prompt
from rag import BasicRAG, AgenticRAG, rag_tool
from prompts.cot_production_prompts import (
    COT_PRODUCTION_SYSTEM_PROMPT,
    format_gather_info_prompt,
    format_query_knowledge_prompt,
    format_analyze_prompt,
    format_reasoning_prompt,
    format_conclude_prompt,
    format_uncertainty_prompt
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
    "法律": [
        {"id": "law-001", "topic": "合同法", "content": "合同是民事主体之间设立、变更、终止民事法律关系的协议。合同的生效需要满足主体适格、意思表示真实等要件。"},
        {"id": "law-002", "topic": "知识产权", "content": "知识产权包括著作权、专利权、商标权等，保护创造性智力成果和商业标识。"},
        {"id": "law-003", "topic": "刑法", "content": "刑法规定犯罪行为及其法律后果，包括刑事责任和刑罚种类。适用罪刑法定、罪责刑相适应等原则。"},
        {"id": "law-004", "topic": "劳动法", "content": "劳动法保护劳动者权益，规定劳动合同、工作时间、工资待遇、社会保险等事项。"}
    ],
    "计算机": [
        {"id": "cs-001", "topic": "算法复杂度", "content": "算法复杂度用大O表示法描述算法效率，包括时间复杂度和空间复杂度。常见复杂度有O(1)、O(n)、O(log n)等。"},
        {"id": "cs-002", "topic": "数据结构", "content": "数据结构是数据组织、管理和存储格式，包括数组、链表、树、图等，不同结构适用于不同场景。"},
        {"id": "cs-003", "topic": "网络协议", "content": "网络协议是通信规则的集合，如TCP/IP协议族。TCP提供可靠传输，UDP提供快速但不可靠的传输。"},
        {"id": "cs-004", "topic": "数据库优化", "content": "数据库优化包括索引优化、查询优化、表结构设计等。需要根据具体场景选择合适的优化策略。"}
    ],
    "通用": [
        {"id": "gen-001", "topic": "问题解决", "content": "问题解决的一般步骤包括:1.明确问题 2.收集信息 3.分析原因 4.制定方案 5.实施方案 6.评估结果"},
        {"id": "gen-002", "topic": "决策方法", "content": "常见决策方法包括利弊分析法、决策矩阵法、德尔菲法等，适用于不同类型的决策问题。"},
        {"id": "gen-003", "topic": "创新思维", "content": "创新思维技术包括头脑风暴、六顶思考帽、SCAMPER等方法，有助于打破思维限制。"},
        {"id": "gen-004", "topic": "项目管理", "content": "项目管理包括范围管理、时间管理、成本管理、质量管理等。需要合理规划和控制项目进度。"}
    ]
}


# =================================================================
# Prompt 模板配置已移至 prompts/cot_production_prompts.py
# =================================================================
# 所有 prompt 模板和格式化函数都在独立的配置文件中管理
# 提高可读性和可维护性，避免代码拼接


# =================================================================
# 状态定义
# =================================================================

class CoTProductionState(TypedDict):
    """CoT 生产级推理状态"""
    question: str  # 原始问题
    domain: str  # 领域类别
    context: Optional[Dict[str, Any]]  # 上下文信息
    required_info: Optional[List[str]]  # 所需信息清单
    relevant_knowledge: Optional[List[Dict[str, Any]]]  # 相关领域知识
    reasoning_steps: List[Dict[str, Any]]  # 推理步骤列表
    alternative_paths: Optional[List[Dict[str, Any]]]  # 替代推理路径
    final_answer: str  # 最终答案
    current_step: int  # 当前步骤编号
    confidence_scores: Optional[Dict[str, float]]  # 置信度评分
    solution: Optional[Dict[str, Any]]  # 解决方案（包含实施步骤和局限性）
    tool_calls: Optional[List[Dict[str, Any]]]  # 工具调用记录
    rag_results: Optional[List[Dict[str, Any]]]  # RAG 检索结果


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


def query_rewrite_tool(query: str, context: str = "") -> Dict[str, Any]:
    """查询重写工具 - 使用 LLM 重写查询以提高检索准确性"""
    from rag import BasicRAG
    rag = BasicRAG()
    # 使用 RAG 的查询重写功能（简化版）
    llm = get_llm(temperature=0.3)
    prompt_text = f"""请重写以下查询以提高检索准确性：

原始查询：{query}
上下文：{context}

返回JSON格式：
{{"rewritten_query": "重写后的查询", "reasoning": "重写原因"}}"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一位专业的查询重写专家。"),
        ("human", prompt_text)
    ])
    
    result = (prompt | llm).invoke({})
    
    try:
        json_str = re.search(r'\{.*\}', result.content, re.DOTALL)
        if json_str:
            rewrite_data = json.loads(json_str.group())
            return {
                "rewritten_query": rewrite_data.get("rewritten_query", query),
                "reasoning": rewrite_data.get("reasoning", "")
            }
    except:
        pass
    
    return {"rewritten_query": query, "reasoning": "保持原查询"}


def calculate_tool(expression: str) -> str:
    """计算工具"""
    try:
        # 安全的数学表达式计算
        allowed_chars = set("0123456789+-*/(). ")
        if all(c in allowed_chars for c in expression):
            result = eval(expression)
            return f"计算结果：{result}"
        else:
            return "错误：表达式包含不允许的字符"
    except Exception as e:
        return f"计算错误：{str(e)}"


def get_time_tool() -> str:
    """获取当前时间工具"""
    return f"当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


# 可用工具列表
AVAILABLE_TOOLS = {
    "query_rewrite": Tool("query_rewrite", "重写查询以提高检索准确性", lambda query, context="": query_rewrite_tool(query, context)),
    "rag_search": Tool("rag_search", "使用RAG检索相关信息", lambda query, mode="agentic": rag_tool(query, mode)),
    "calculate": Tool("calculate", "执行数学计算", lambda expr: calculate_tool(expr)),
    "get_time": Tool("get_time", "获取当前时间", lambda: get_time_tool())
}


# =================================================================
# 节点函数
# =================================================================

def gather_information_node(state: CoTProductionState) -> Dict[str, Any]:
    """信息收集节点 - 分析问题需求，判断是否需要工具调用"""
    
    log_node_input("gather_information_node", state)
    
    question = state["question"]
    domain = state.get("domain", "通用")
    context = state.get("context", {})
    tool_calls = state.get("tool_calls", [])
    
    # 判断是否需要查询重写（对于复杂查询）
    needs_query_rewrite = len(question) > 50 or any(keyword in question for keyword in ["如何", "为什么", "解释"])
    rewritten_query = question
    
    if needs_query_rewrite:
        try:
            rewrite_result = AVAILABLE_TOOLS["query_rewrite"].execute(query=question, context=json.dumps(context, ensure_ascii=False))
            rewritten_query = rewrite_result.get("rewritten_query", question)
            tool_calls.append({
                "tool": "query_rewrite",
                "input": question,
                "output": rewrite_result,
                "timestamp": datetime.now().isoformat()
            })
            print(f"  [工具调用] query_rewrite: {question[:50]}... -> {rewritten_query[:50]}...")
        except Exception as e:
            print(f"  [工具调用失败] query_rewrite: {str(e)}")
    
    llm = get_llm(temperature=0.3)
    
    # 格式化 Prompt（使用重写后的查询）
    human_prompt = format_gather_info_prompt(
        question=rewritten_query,
        domain=domain,
        context=json.dumps(context, ensure_ascii=False)
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一位专业的问题分析专家，擅长分析复杂问题并确定解决问题所需的关键信息。"),
        ("human", human_prompt)
    ])
    
    log_prompt("gather_information_node", [
        ("system", "你是一位专业的问题分析专家，擅长分析复杂问题并确定解决问题所需的关键信息。"),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析结果
    try:
        json_str = re.search(r'\{.*\}', result.content, re.DOTALL)
        if json_str:
            analysis = json.loads(json_str.group())
        else:
            analysis = {"required_info": [], "problem_classification": domain, "complexity": 5}
    except:
        analysis = {"required_info": [], "problem_classification": domain, "complexity": 5}
    
    required_info = analysis.get("required_info", [])
    if isinstance(required_info, str):
        required_info = [required_info]
    
    output = {
        "required_info": required_info,
        "tool_calls": tool_calls if tool_calls else None,
        "context": {
            **context,
            "problem_classification": analysis.get("problem_classification", domain),
            "complexity": analysis.get("complexity", 5),
            "rewritten_query": rewritten_query if needs_query_rewrite else None
        }
    }
    
    log_node_output("gather_information_node", output)
    
    return output


def query_knowledge_base_node(state: CoTProductionState) -> Dict[str, Any]:
    """知识检索节点 - 获取领域相关知识（支持 RAG 和传统知识库）"""
    
    log_node_input("query_knowledge_base_node", state)
    
    question = state["question"]
    domain = state.get("domain", "通用")
    required_info = state.get("required_info", [])
    context = state.get("context", {})
    tool_calls = state.get("tool_calls", [])
    
    # 使用重写后的查询（如果有）
    search_query = context.get("rewritten_query", question)
    
    # 初始化 rag_results
    rag_results = state.get("rag_results", [])
    
    # 判断是否需要 RAG 检索（如果传统知识库可能不够或问题较复杂）
    use_rag = context.get("complexity", 5) >= 6 or any(keyword in question.lower() for keyword in ["最新", "当前", "实时", "检索", "搜索"])
    
    if use_rag:
        try:
            rag_result = AVAILABLE_TOOLS["rag_search"].execute(query=search_query, mode="agentic")
            rag_results.append({
                "query": search_query,
                "result": rag_result,
                "timestamp": datetime.now().isoformat()
            })
            tool_calls.append({
                "tool": "rag_search",
                "input": search_query,
                "output": rag_result.get("answer", "")[:200] if isinstance(rag_result, dict) else str(rag_result)[:200],
                "timestamp": datetime.now().isoformat()
            })
            print(f"  [工具调用] rag_search: {search_query[:50]}...")
        except Exception as e:
            print(f"  [工具调用失败] rag_search: {str(e)}")
    
    # 从知识库检索
    knowledge_entries = KNOWLEDGE_BASE.get(domain, KNOWLEDGE_BASE["通用"])
    
    if not knowledge_entries:
        output = {"relevant_knowledge": []}
        log_node_output("query_knowledge_base_node", output)
        return output
    
    # 准备知识文本
    knowledge_texts = []
    for entry in knowledge_entries:
        knowledge_texts.append(f"ID: {entry['id']}\n主题: {entry['topic']}\n内容: {entry['content']}")
    
    knowledge_text = "\n\n".join(knowledge_texts)
    
    llm = get_llm(temperature=0.2)
    
    # 格式化 Prompt
    human_prompt = format_query_knowledge_prompt(
        question=question,
        domain=domain,
        required_info=json.dumps(required_info, ensure_ascii=False),
        knowledge_text=knowledge_text
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一位专业的知识评估专家，擅长评估知识与问题的相关性。"),
        ("human", human_prompt)
    ])
    
    log_prompt("query_knowledge_base_node", [
        ("system", "你是一位专业的知识评估专家，擅长评估知识与问题的相关性。"),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析结果
    try:
        json_str = re.search(r'\{.*\}', result.content, re.DOTALL)
        if json_str:
            relevance_result = json.loads(json_str.group())
        else:
            relevance_result = {"relevant_entries": []}
    except:
        relevance_result = {"relevant_entries": []}
    
    # 合并相关知识
    relevant_entries = relevance_result.get("relevant_entries", [])
    relevant_knowledge = []
    
    for entry in relevant_entries:
        entry_id = entry.get("id")
        for k_entry in knowledge_entries:
            if k_entry["id"] == entry_id:
                relevant_knowledge.append({
                    "id": entry_id,
                    "topic": k_entry["topic"],
                    "content": k_entry["content"],
                    "relevance_score": entry.get("relevance_score", 5),
                    "relevance_explanation": entry.get("relevance_explanation", "")
                })
                break
    
    # 按相关性排序
    relevant_knowledge.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    # 更新重试次数
    context = state.get("context", {})
    retry_count = context.get("knowledge_retry_count", 0)
    
    output = {
        "relevant_knowledge": relevant_knowledge,
        "rag_results": rag_results if rag_results else None,
        "tool_calls": tool_calls if tool_calls else None,
        "context": {
            **context,
            "knowledge_retry_count": retry_count + 1
        }
    }
    
    log_node_output("query_knowledge_base_node", output)
    
    return output


def analyze_question_node(state: CoTProductionState) -> Dict[str, Any]:
    """分析问题节点 - 提取关键信息"""
    
    log_node_input("analyze_question_node", state)
    
    question = state["question"]
    domain = state.get("domain", "通用")
    relevant_knowledge = state.get("relevant_knowledge", [])
    
    # 准备知识文本
    knowledge_text = ""
    for i, entry in enumerate(relevant_knowledge[:5], 1):  # 最多使用5条知识
        knowledge_text += f"\n知识{i}: [{entry['topic']}] {entry['content']}"
    
    if not knowledge_text:
        knowledge_text = "无相关领域知识"
    
    llm = get_llm(temperature=0.3)
    
    # 格式化 Prompt
    human_prompt = format_analyze_prompt(
        question=question,
        domain=domain,
        knowledge=knowledge_text
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", COT_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    log_prompt("analyze_question_node", [
        ("system", COT_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析结果
    try:
        json_str = re.search(r'\{.*\}', result.content, re.DOTALL)
        if json_str:
            analysis = json.loads(json_str.group())
        else:
            analysis = {"key_elements": [], "constraints": [], "analysis": result.content}
    except:
        analysis = {"key_elements": [], "constraints": [], "analysis": result.content}
    
    reasoning_step = {
        "step_number": 1,
        "step_name": "问题分析",
        "content": analysis.get("analysis", ""),
        "key_elements": analysis.get("key_elements", []),
        "reasoning": "提取问题的关键要素和约束条件，结合领域知识进行初步分析"
    }
    
    output = {
        "reasoning_steps": [reasoning_step],
        "current_step": 1
    }
    
    log_node_output("analyze_question_node", output)
    
    return output


def reasoning_node(state: CoTProductionState) -> Dict[str, Any]:
    """推理节点 - 逐步推理，支持工具调用"""
    
    log_node_input("reasoning_node", state)
    
    question = state["question"]
    domain = state.get("domain", "通用")
    reasoning_steps = state.get("reasoning_steps", [])
    current_step = state.get("current_step", 1)
    relevant_knowledge = state.get("relevant_knowledge", [])
    tool_calls = state.get("tool_calls", [])
    
    # 构建已有推理步骤的上下文
    context = ""
    for step in reasoning_steps:
        context += f"\n步骤{step['step_number']}: {step['step_name']}\n"
        context += f"内容: {step['content']}\n"
    
    # 检测是否需要计算工具（在推理内容中检测数学表达式）
    # 注意：这里只是示例，实际应该在 LLM 返回后检测
    
    # 准备知识文本
    knowledge_text = ""
    for i, entry in enumerate(relevant_knowledge[:5], 1):
        knowledge_text += f"\n知识{i}: [{entry['topic']}] {entry['content']}"
    
    if not knowledge_text:
        knowledge_text = "无相关领域知识"
    
    # 计算剩余推理步骤
    max_steps = 3  # 最多3步推理
    remaining_steps = max_steps - current_step
    is_last_step = remaining_steps <= 1
    
    llm = get_llm(temperature=0.3)
    
    # 格式化 Prompt
    human_prompt = format_reasoning_prompt(
        question=question,
        context=context,
        knowledge=knowledge_text,
        current_step=current_step,
        max_steps=max_steps,
        remaining_steps=remaining_steps,
        is_last_step=is_last_step
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", COT_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    log_prompt("reasoning_node", [
        ("system", COT_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析结果
    try:
        json_str = re.search(r'\{.*\}', result.content, re.DOTALL)
        if json_str:
            step_data = json.loads(json_str.group())
        else:
            step_data = {
                "step_name": f"步骤{current_step + 1}",
                "content": result.content,
                "reasoning": "",
                "next_action": "",
                "can_conclude": False
            }
    except:
        step_data = {
            "step_name": f"步骤{current_step + 1}",
            "content": result.content,
            "reasoning": "",
            "next_action": "",
            "can_conclude": False
        }
    
    new_step = {
        "step_number": current_step + 1,
        "step_name": step_data.get("step_name", f"步骤{current_step + 1}"),
        "content": step_data.get("content", ""),
        "reasoning": step_data.get("reasoning", ""),
        "next_action": step_data.get("next_action", ""),
        "can_conclude": step_data.get("can_conclude", False)
    }
    
    reasoning_steps.append(new_step)
    
    # 检测推理内容中是否需要计算工具
    step_content = new_step.get("content", "")
    # 检测数学表达式模式（简单检测）
    math_pattern = r'\d+\s*[+\-*/]\s*\d+|计算|等于|结果'
    if re.search(math_pattern, step_content):
        # 尝试提取数学表达式
        expressions = re.findall(r'(\d+\s*[+\-*/]\s*\d+)', step_content)
        for expr in expressions[:1]:  # 只处理第一个表达式
            try:
                calc_result = AVAILABLE_TOOLS["calculate"].execute(expression=expr)
                tool_calls.append({
                    "tool": "calculate",
                    "input": expr,
                    "output": calc_result,
                    "timestamp": datetime.now().isoformat()
                })
                print(f"  [工具调用] calculate: {expr} = {calc_result}")
                # 将计算结果添加到推理步骤中
                new_step["content"] += f"\n[计算结果: {calc_result}]"
            except Exception as e:
                print(f"  [工具调用失败] calculate: {str(e)}")
    
    # 提取替代路径（如果存在）
    alternative_paths = state.get("alternative_paths") or []  # 确保不为 None
    if step_data.get("alternative_paths"):
        # 合并替代路径，避免重复
        existing_descriptions = {path.get("description", "") for path in alternative_paths}
        for alt_path in step_data.get("alternative_paths", []):
            if alt_path.get("description", "") not in existing_descriptions:
                alternative_paths.append(alt_path)
    
    output = {
        "reasoning_steps": reasoning_steps,
        "current_step": current_step + 1,
        "alternative_paths": alternative_paths if alternative_paths else None,
        "tool_calls": tool_calls if tool_calls else None
    }
    
    log_node_output("reasoning_node", output)
    
    return output


def conclude_node(state: CoTProductionState) -> Dict[str, Any]:
    """结论节点 - 得出最终答案"""
    
    log_node_input("conclude_node", state)
    
    question = state["question"]
    domain = state.get("domain", "通用")
    reasoning_steps = state.get("reasoning_steps", [])
    relevant_knowledge = state.get("relevant_knowledge", [])
    alternative_paths = state.get("alternative_paths", [])
    
    # 构建完整推理过程
    context = ""
    for step in reasoning_steps:
        context += f"\n步骤{step['step_number']}: {step['step_name']}\n"
        context += f"内容: {step['content']}\n"
        if step.get('reasoning'):
            context += f"推理依据: {step['reasoning']}\n"
    
    # 准备知识文本
    knowledge_text = ""
    for i, entry in enumerate(relevant_knowledge[:5], 1):
        knowledge_text += f"\n知识{i}: [{entry['topic']}] {entry['content']}"
    
    if not knowledge_text:
        knowledge_text = "无相关领域知识"
    
    # 准备替代路径文本
    alternative_paths_text = ""
    if alternative_paths:
        for i, path in enumerate(alternative_paths, 1):
            alternative_paths_text += f"\n替代路径{i}: {path.get('description', '')}\n"
            alternative_paths_text += f"  推理: {path.get('reasoning', '')}\n"
            if path.get('pros'):
                alternative_paths_text += f"  优点: {path.get('pros', '')}\n"
            if path.get('cons'):
                alternative_paths_text += f"  缺点: {path.get('cons', '')}\n"
    
    llm = get_llm(temperature=0.3)
    
    # 格式化 Prompt
    human_prompt = format_conclude_prompt(
        question=question,
        context=context,
        knowledge=knowledge_text,
        alternative_paths=alternative_paths_text
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", COT_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    log_prompt("conclude_node", [
        ("system", COT_PRODUCTION_SYSTEM_PROMPT),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析结果
    try:
        json_str = re.search(r'\{.*\}', result.content, re.DOTALL)
        if json_str:
            conclusion = json.loads(json_str.group())
        else:
            conclusion = {
                "final_answer": result.content,
                "summary": "",
                "confidence": "中",
                "explanation": "",
                "implementation_steps": [],
                "limitations": []
            }
    except:
        conclusion = {
            "final_answer": result.content,
            "summary": "",
            "confidence": "中",
            "explanation": "",
            "implementation_steps": [],
            "limitations": []
        }
    
    # 确保 implementation_steps 和 limitations 是列表
    implementation_steps = conclusion.get("implementation_steps", [])
    if isinstance(implementation_steps, str):
        implementation_steps = [implementation_steps] if implementation_steps else []
    
    limitations = conclusion.get("limitations", [])
    if isinstance(limitations, str):
        limitations = [limitations] if limitations else []
    
    solution = {
        "main_solution": conclusion.get("final_answer", result.content),
        "summary": conclusion.get("summary", ""),
        "confidence": conclusion.get("confidence", "中"),
        "explanation": conclusion.get("explanation", ""),
        "implementation_steps": implementation_steps,
        "limitations": limitations
    }
    
    output = {
        "final_answer": conclusion.get("final_answer", result.content),
        "solution": solution,
        "alternative_paths": alternative_paths if alternative_paths else None,
        "reasoning_steps": reasoning_steps + [{
            "step_number": len(reasoning_steps) + 1,
            "step_name": "最终结论",
            "content": conclusion.get("final_answer", ""),
            "summary": conclusion.get("summary", ""),
            "confidence": conclusion.get("confidence", "中")
        }]
    }
    
    log_node_output("conclude_node", output)
    
    return output


def handle_uncertainty_node(state: CoTProductionState) -> Dict[str, Any]:
    """不确定性处理节点 - 评估推理的置信度"""
    
    log_node_input("handle_uncertainty_node", state)
    
    reasoning_steps = state.get("reasoning_steps", [])
    solution = state.get("solution", {})
    
    if not reasoning_steps:
        output = {
            "confidence_scores": {
                "overall": 0.5,
                "completeness": 0.5,
                "consistency": 0.5,
                "evidence_strength": 0.5
            }
        }
        log_node_output("handle_uncertainty_node", output)
        return output
    
    # 准备推理步骤文本
    reasoning_text = ""
    for step in reasoning_steps:
        reasoning_text += f"\n步骤{step.get('step_number', '?')}: {step.get('step_name', '')}\n"
        reasoning_text += f"推理: {step.get('content', '')}\n"
    
    solution_text = json.dumps(solution, ensure_ascii=False)
    
    llm = get_llm(temperature=0.2)
    
    # 格式化 Prompt
    human_prompt = format_uncertainty_prompt(
        reasoning=reasoning_text,
        solution=solution_text
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一位专业的不确定性分析专家，擅长识别和量化推理过程中的不确定因素。"),
        ("human", human_prompt)
    ])
    
    log_prompt("handle_uncertainty_node", [
        ("system", "你是一位专业的不确定性分析专家，擅长识别和量化推理过程中的不确定因素。"),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析结果
    try:
        json_str = re.search(r'\{.*\}', result.content, re.DOTALL)
        if json_str:
            uncertainty_result = json.loads(json_str.group())
        else:
            uncertainty_result = {
                "confidence_scores": {
                    "overall": 0.7,
                    "completeness": 0.7,
                    "consistency": 0.8,
                    "evidence_strength": 0.7
                },
                "uncertainty_sources": [],
                "recommendations": []
            }
    except:
        uncertainty_result = {
            "confidence_scores": {
                "overall": 0.7,
                "completeness": 0.7,
                "consistency": 0.8,
                "evidence_strength": 0.7
            },
            "uncertainty_sources": [],
            "recommendations": []
        }
    
    confidence_scores = uncertainty_result.get("confidence_scores", {})
    
    output = {
        "confidence_scores": confidence_scores,
        "context": {
            **(state.get("context", {})),
            "uncertainty_sources": uncertainty_result.get("uncertainty_sources", []),
            "uncertainty_recommendations": uncertainty_result.get("recommendations", [])
        }
    }
    
    log_node_output("handle_uncertainty_node", output)
    
    return output


def should_continue_reasoning(state: CoTProductionState) -> str:
    """判断是否继续推理"""
    current_step = state.get("current_step", 1)
    reasoning_steps = state.get("reasoning_steps", [])
    
    # 检查是否已经达到最大步数（最多3步推理）
    if current_step >= 3:
        return "conclude"
    
    # 检查最近的推理步骤是否表示可以提前结束
    if reasoning_steps:
        last_step = reasoning_steps[-1]
        # 如果 LLM 明确表示可以结束推理
        if last_step.get("can_conclude", False):
            return "conclude"
        # 如果 next_action 明确表示可以得出最终答案
        next_action = last_step.get("next_action", "").lower()
        if "得出最终答案" in next_action or "conclude" in next_action or "结束" in next_action:
            return "conclude"
    
    return "reason"


def uncertainty_route(state: CoTProductionState) -> str:
    """不确定性路由函数 - 基于置信度决定下一步"""
    confidence_scores = state.get("confidence_scores", {})
    overall_confidence = confidence_scores.get("overall", 0.0)
    context = state.get("context", {})
    
    # 获取重试次数
    retry_count = context.get("knowledge_retry_count", 0)
    max_retries = 2  # 最多重试2次
    
    # 如果置信度够高（>= 0.6），结束流程
    if overall_confidence >= 0.6:
        return "end"
    elif retry_count < max_retries:
        # 置信度不够，且未达到最大重试次数，重新检索知识
        # 更新重试次数
        return "query_knowledge_base"
    else:
        # 达到最大重试次数，即使置信度不够也结束
        return "end"


# =================================================================
# 构建图
# =================================================================

def create_cot_production_graph():
    """创建 CoT 生产级推理图"""
    
    graph = StateGraph(CoTProductionState)
    
    # 添加节点
    # 1. 信息收集节点：分析问题需求，确定解决问题所需的关键信息，判断是否需要工具调用和RAG检索
    graph.add_node("gather_information", gather_information_node)
    
    # 2. 知识检索节点：获取领域相关知识，支持传统知识库和RAG检索（基础RAG/Agentic RAG/LLM RAG）
    graph.add_node("query_knowledge_base", query_knowledge_base_node)
    
    # 3. 问题分析节点：基于检索到的知识，提取问题的关键要素和约束条件，进行初步分析
    graph.add_node("analyze", analyze_question_node)
    
    # 4. 推理节点：逐步推理，基于已有推理步骤和相关知识进行下一步推理（可循环最多3次，支持提前结束）
    graph.add_node("reason", reasoning_node)
    
    # 5. 结论节点：基于完整的推理过程和相关知识，生成最终答案和解决方案
    graph.add_node("conclude", conclude_node)
    
    # 6. 不确定性处理节点：评估推理过程和解决方案的置信度，决定是否需要重新检索知识以提高可靠性（支持循环改进，最多重试2次）
    graph.add_node("handle_uncertainty", handle_uncertainty_node)
    
    # 设置流程
    graph.set_entry_point("gather_information")
    graph.add_edge("gather_information", "query_knowledge_base")
    graph.add_edge("query_knowledge_base", "analyze")
    graph.add_edge("analyze", "reason")
    graph.add_conditional_edges(
        "reason",
        should_continue_reasoning,
        {
            "reason": "reason",  # 继续推理
            "conclude": "conclude"  # 得出结论
        }
    )
    graph.add_edge("conclude", "handle_uncertainty")
    graph.add_conditional_edges(
        "handle_uncertainty",
        uncertainty_route,
        {
            "end": END,
            "query_knowledge_base": "query_knowledge_base"  # 重新检索知识
        }
    )
    
    return graph.compile()


# =================================================================
# Demo 示例
# =================================================================

def demo_cot_production():
    """CoT 生产级推理 Demo"""
    
    print("=" * 60)
    print("Chain-of-Thought (CoT) 生产级推理 Demo")
    print("=" * 60)
    
    # 创建图
    graph = create_cot_production_graph()
    
    # 测试问题
    test_cases = [
        {
            "question": "患者出现持续高血压，收缩压150mmHg，舒张压95mmHg，伴有轻微头痛，该如何处理？",
            "domain": "医学",
            "context": {"patient_age": 45, "patient_gender": "男"}
        },
        # {
        #     "question": "一个包含10万条记录的数据库查询非常缓慢，如何优化性能？",
        #     "domain": "计算机",
        #     "context": {"database_type": "MySQL", "current_response_time": "15秒"}
        # },
        # {
        #     "question": "团队成员之间沟通不畅，影响项目进度，如何改善团队协作？",
        #     "domain": "通用",
        #     "context": {"team_size": 8, "project_duration": "6个月"}
        # }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n【测试案例 {i}】")
        print(f"问题：{test_case['question']}")
        print(f"领域：{test_case['domain']}")
        print(f"上下文：{json.dumps(test_case['context'], ensure_ascii=False)}\n")
        
        # 运行推理
        initial_state = {
            "question": test_case["question"],
            "domain": test_case["domain"],
            "context": test_case["context"],
            "required_info": None,
            "relevant_knowledge": None,
            "reasoning_steps": [],
            "alternative_paths": None,
            "final_answer": "",
            "current_step": 0,
            "confidence_scores": None,
            "solution": None
        }
        
        result = graph.invoke(initial_state)
        
        # 显示结果
        print("\n" + "=" * 60)
        print("推理结果")
        print("=" * 60)
        
        # 显示所需信息
        if result.get("required_info"):
            print("\n【所需信息】")
            for j, info in enumerate(result.get("required_info"), 1):
                print(f"{j}. {info}")
        
        # 显示相关知识
        if result.get("relevant_knowledge"):
            print("\n【相关知识】")
            for j, knowledge in enumerate(result.get("relevant_knowledge")[:3], 1):
                print(f"{j}. [{knowledge['topic']}] (相关性: {knowledge.get('relevance_score', 0)}/10)")
                print(f"   {knowledge['content'][:100]}...")
        
        # 显示推理过程
        print("\n【推理过程】")
        for step in result.get("reasoning_steps", []):
            print(f"\n步骤 {step['step_number']}: {step['step_name']}")
            print(f"  内容: {step['content']}")
            if step.get('reasoning'):
                print(f"  推理依据: {step['reasoning']}")
        
        # 显示最终答案
        print(f"\n【最终答案】")
        print(result.get('final_answer', '未生成'))
        
        # 显示解决方案详情
        solution = result.get("solution", {})
        if solution:
            if solution.get("explanation"):
                print(f"\n【解决方案解释】")
                print(solution.get("explanation"))
            
            if solution.get("implementation_steps"):
                print(f"\n【实施步骤】")
                for j, step in enumerate(solution.get("implementation_steps", []), 1):
                    print(f"  {j}. {step}")
            
            if solution.get("limitations"):
                print(f"\n【局限性和注意事项】")
                for j, limitation in enumerate(solution.get("limitations", []), 1):
                    print(f"  {j}. {limitation}")
        
        # 显示替代推理路径
        if result.get("alternative_paths"):
            print(f"\n【替代推理路径】")
            for j, path in enumerate(result.get("alternative_paths", []), 1):
                print(f"\n  路径 {j}: {path.get('description', '未提供')}")
                if path.get('reasoning'):
                    print(f"    推理: {path.get('reasoning')}")
                if path.get('pros'):
                    print(f"    优点: {path.get('pros')}")
                if path.get('cons'):
                    print(f"    缺点: {path.get('cons')}")
        
        # 显示置信度评估
        if result.get("confidence_scores"):
            print("\n【置信度评估】")
            confidence_scores = result.get("confidence_scores", {})
            for aspect, score in confidence_scores.items():
                print(f"  {aspect}: {score:.2f}")
        
        # 显示工具调用记录
        if result.get("tool_calls"):
            print("\n【工具调用记录】")
            for j, tool_call in enumerate(result.get("tool_calls", []), 1):
                print(f"  {j}. [{tool_call.get('tool', 'unknown')}]")
                input_str = str(tool_call.get('input', ''))
                print(f"     输入: {input_str[:100]}")
                output_val = tool_call.get('output', '')
                if isinstance(output_val, dict):
                    output_str = json.dumps(output_val, ensure_ascii=False)[:200]
                else:
                    output_str = str(output_val)[:200]
                print(f"     输出: {output_str}")
        
        print("\n" + "-" * 60)


if __name__ == "__main__":
    demo_cot_production()
