from typing import Dict
from langchain_core.prompts import ChatPromptTemplate
from agent_proj.graph.state import AgentState
from agent_proj.utils import get_llm
from agent_proj.prompts import get_reflection_prompts, get_node_config
import json
import re

def reflection_node(state: AgentState) -> Dict:
    """
    Reflection Node: 反思推理质量，检测逻辑错误
    
    检查项：
    1. 推理步骤是否合理
    2. 是否有逻辑跳跃
    3. 证据使用是否恰当
    4. 结论是否过度推断
    """
    reasoning_steps = state.get("analyst_reasoning_steps", [])
    findings = state.get("research_findings", [])
    topic = state.get("topic", "")
    
    if not reasoning_steps:
        return {
            "reflection_passed": True,
            "reflection_issues": []
        }
    
    config = get_node_config("reflection")
    llm = get_llm(temperature=config["temperature"], model_name=config["model"])
    
    # 构建推理步骤摘要
    reasoning_summary = "\n\n".join([
        f"**步骤{step['step_number']}: {step['step_name']}**\n"
        f"推理: {step.get('reasoning', '')[:200]}...\n"
        f"结论: {step.get('content', '')[:200]}...\n"
        f"证据引用: {step.get('evidence_refs', [])}"
        for step in reasoning_steps
    ])
    
    # Get prompts from centralized prompt management
    prompts = get_reflection_prompts(
        topic=topic,
        reasoning_summary=reasoning_summary,
        findings_count=len(findings)
    )
    
    reflection_prompt = ChatPromptTemplate.from_messages([
        ("system", prompts["system"]),
        ("human", prompts["user"])
    ])
    
    chain = reflection_prompt | llm
    result = chain.invoke({})
    
    # 解析反思结果
    try:
        json_match = re.search(r'\{.*\}', result.content, re.DOTALL)
        if json_match:
            reflection = json.loads(json_match.group())
        else:
            reflection = {
                "is_valid": True,
                "issues": [],
                "suggestions": [],
                "confidence": 0.8
            }
    except:
        reflection = {
            "is_valid": True,
            "issues": [],
            "suggestions": [],
            "confidence": 0.8
        }
    
    # 判断是否需要重新推理
    is_valid = reflection.get("is_valid", True)
    confidence = reflection.get("confidence", 0.8)
    
    # 如果发现严重问题或置信度过低，需要重新推理
    needs_rethink = not is_valid or confidence < 0.6
    
    return {
        "reflection_passed": not needs_rethink,
        "reflection_issues": reflection.get("issues", []),
        "reflection_suggestions": reflection.get("suggestions", []),
        "reasoning_confidence": confidence
    }
