from typing import Dict, List
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from agent_proj.graph.state import AgentState
from agent_proj.utils import get_llm
from agent_proj.prompts import get_analyst_step_prompts, get_report_generation_prompts, get_node_config
import json
import re

def analyst_node(state: AgentState) -> Dict:
    """
    L3 Analyst Node: 基于 CoT 范式生成深度报告
    使用显式的多步推理，每步都有明确的推理依据
    """
    findings = state.get("research_findings", [])
    topic = state.get("topic")
    
    if not findings:
        return {
            "final_report": "没有足够的研究发现生成报告。",
            "analyst_reasoning_steps": []
        }
    
    # 1. 构建 Evidence Pool (事实池)
    evidence_pool = {}
    for i, fact in enumerate(findings, 1):
        evidence_pool[i] = {
            "content": fact.content,
            "source": fact.source_url
        }
    
    evidence_text = "\n".join([f"[{k}] {v['content'][:200]}... (Source: {v['source']})" 
                               for k, v in evidence_pool.items()])
    
    config = get_node_config("analyst")
    llm = get_llm(temperature=config["temperature"], model_name=config["model"])
    
    reasoning_steps = []
    
    # 2. 多步推理 (CoT)
    reasoning_topics = [
        {"step_name": "市场规模分析", "focus": "分析市场定义和规模"},
        {"step_name": "竞争格局分析", "focus": "分析主要竞争者和市场份额"},
        {"step_name": "趋势与驱动因素", "focus": "分析行业趋势和增长动力"}
    ]
    
    for i, topic_def in enumerate(reasoning_topics, 1):
        # Get prompts from centralized prompt management
        prompts = get_analyst_step_prompts(
            focus=topic_def['focus'],
            evidence_text=evidence_text,
            step_name=topic_def['step_name']
        )
        
        step_prompt = ChatPromptTemplate.from_messages([
            ("system", prompts["system"]),
            ("human", prompts["user"])
        ])
        
        chain = step_prompt | llm
        result = chain.invoke({})
        
        # 解析结果
        try:
            json_match = re.search(r'\{.*\}', result.content, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
            else:
                parsed = {
                    "reasoning": result.content,
                    "conclusion": "",
                    "evidence_refs": []
                }
        except:
            parsed = {
                "reasoning": result.content,
                "conclusion": "",
                "evidence_refs": []
            }
        
        reasoning_steps.append({
            "step_number": i,
            "step_name": topic_def["step_name"],
            "content": parsed.get("conclusion", parsed.get("reasoning", "")),
            "reasoning": parsed.get("reasoning", ""),
            "evidence_refs": parsed.get("evidence_refs", [])
        })
    
    # 3. 生成最终报告
    reasoning_summary = "\n\n".join([
        f"### {step['step_name']}\n{step['content']}\n推理过程: {step['reasoning']}"
        for step in reasoning_steps
    ])
    
    # Get prompts from centralized prompt management
    prompts = get_report_generation_prompts(
        topic=topic,
        reasoning_summary=reasoning_summary,
        evidence_text=evidence_text
    )
    
    final_prompt = ChatPromptTemplate.from_messages([
        ("system", prompts["system"]),
        ("human", prompts["user"])
    ])
    
    chain = final_prompt | llm
    final_result = chain.invoke({})
    
    # Increment retry count if this is a regeneration
    current_retry = state.get("retry_count", 0)
    if state.get("needs_regenerate", False):
        current_retry += 1
    
    return {
        "analyst_reasoning_steps": reasoning_steps,
        "final_report": final_result.content,
        "retry_count": current_retry,
        "needs_regenerate": False  # Reset flag
    }
