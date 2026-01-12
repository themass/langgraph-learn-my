from typing import Dict
from langchain_core.prompts import ChatPromptTemplate
from agent_proj.graph.state import AgentState
from agent_proj.utils import get_llm
from agent_proj.prompts import get_uncertainty_prompts, get_node_config
import json
import re

def uncertainty_handling_node(state: AgentState) -> Dict:
    """
    Uncertainty Handling Node: 处理不确定性，评估答案可信度
    
    评估维度：
    1. 证据充分性
    2. 推理可靠性
    3. 信息来源质量
    4. 结论明确性
    """
    final_report = state.get("final_report", "")
    findings = state.get("research_findings", [])
    reasoning_steps = state.get("analyst_reasoning_steps", [])
    reasoning_confidence = state.get("reasoning_confidence", 0.8)
    topic = state.get("topic", "")
    
    config = get_node_config("uncertainty")
    llm = get_llm(temperature=config["temperature"], model_name=config["model"])
    
    # 构建评估上下文
    findings_summary = f"共 {len(findings)} 条研究发现"
    reasoning_summary = f"共 {len(reasoning_steps)} 步推理"
    
    # Get prompts from centralized prompt management
    prompts = get_uncertainty_prompts(
        topic=topic,
        findings_summary=findings_summary,
        reasoning_summary=reasoning_summary,
        reasoning_confidence=reasoning_confidence,
        report_excerpt=final_report[:500] + "..."
    )
    
    uncertainty_prompt = ChatPromptTemplate.from_messages([
        ("system", prompts["system"]),
        ("human", prompts["user"])
    ])
    
    chain = uncertainty_prompt | llm
    result = chain.invoke({})
    
    # 解析不确定性评估
    try:
        json_match = re.search(r'\{.*\}', result.content, re.DOTALL)
        if json_match:
            uncertainty = json.loads(json_match.group())
        else:
            uncertainty = {
                "overall_confidence": reasoning_confidence,
                "confidence_breakdown": {},
                "uncertainties": [],
                "needs_more_info": False
            }
    except:
        uncertainty = {
            "overall_confidence": reasoning_confidence,
            "confidence_breakdown": {},
            "uncertainties": [],
            "needs_more_info": False
        }
    
    overall_confidence = uncertainty.get("overall_confidence", 0.8)
    needs_more_info = uncertainty.get("needs_more_info", False)
    
    # 判断是否需要重新执行（获取更多信息）
    # 如果置信度过低且判断需要更多信息，可以触发重新规划
    needs_replan_for_info = overall_confidence < 0.5 and needs_more_info
    
    return {
        "overall_confidence": overall_confidence,
        "confidence_breakdown": uncertainty.get("confidence_breakdown", {}),
        "uncertainty_sources": uncertainty.get("uncertainties", []),
        "needs_more_information": needs_more_info,
        "uncertainty_handled": True
    }
