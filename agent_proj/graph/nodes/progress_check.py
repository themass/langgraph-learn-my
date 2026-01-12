from typing import Dict
from langchain_core.prompts import ChatPromptTemplate
from agent_proj.graph.state import AgentState
from agent_proj.utils import get_llm
from agent_proj.prompts import get_progress_check_prompts, get_node_config
import json
import re

def progress_check_node(state: AgentState) -> Dict:
    """
    Progress Check Node: 评估任务执行进度，判断是否需要重新规划
    这是 Plan-and-Execute 范式的核心组件
    """
    topic = state.get("topic")
    plan = state.get("plan", [])
    current_idx = state.get("current_step_index", 0)
    findings = state.get("research_findings", [])
    
    if not plan or current_idx >= len(plan):
        return {
            "needs_replan": False,
            "progress_assessment": {"status": "no_check_needed"}
        }
    
    config = get_node_config("progress_check")
    llm = get_llm(temperature=config["temperature"], model_name=config["model"])
    
    # 构建评估上下文
    plan_summary = "\n".join([
        f"{i+1}. {step.description} (Status: {step.status})"
        for i, step in enumerate(plan)
    ])
    
    findings_summary = "\n".join([
        f"- {fact.content[:100]}..."
        for fact in findings[:5]  # 只显示最近5条
    ]) if findings else "暂无发现"
    
    # Get prompts from centralized prompt management
    prompts = get_progress_check_prompts(
        topic=topic,
        plan_summary=plan_summary,
        current_idx=current_idx,
        total_plan=len(plan),
        findings_summary=findings_summary
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompts["system"]),
        ("human", prompts["user"])
    ])
    
    chain = prompt | llm
    result = chain.invoke({})
    
    # 解析评估结果
    try:
        json_match = re.search(r'\{.*\}', result.content, re.DOTALL)
        if json_match:
            assessment = json.loads(json_match.group())
        else:
            assessment = {
                "on_track": True,
                "needs_replan": False,
                "reason": "无法解析评估结果",
                "suggestions": []
            }
    except:
        assessment = {
            "on_track": True,
            "needs_replan": False,
            "reason": "解析失败",
            "suggestions": []
        }
    
    return {
        "needs_replan": assessment.get("needs_replan", False),
        "progress_assessment": assessment
    }
