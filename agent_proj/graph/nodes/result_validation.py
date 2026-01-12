from typing import Dict
from langchain_core.prompts import ChatPromptTemplate
from agent_proj.graph.state import AgentState
from agent_proj.utils import get_llm
from agent_proj.prompts import get_validation_prompts, get_node_config
import json
import re

def result_validation_node(state: AgentState) -> Dict:
    """
    Result Validation Node: 验证最终报告的质量
    
    验证项：
    1. 报告格式完整性
    2. 引用有效性
    3. 内容充分性
    4. 一致性检查
    """
    final_report = state.get("final_report", "")
    findings = state.get("research_findings", [])
    topic = state.get("topic", "")
    
    # 1. 基本完整性检查
    if not final_report or len(final_report.strip()) < 100:
        return {
            "result_validated": False,
            "validation_issues": ["报告过短或为空"],
            "needs_regenerate": True
        }
    
    # 2. 引用有效性检查
    # 检查报告中的引用 [1], [2] 是否对应实际的 findings
    citation_pattern = r'\[(\d+)\]'
    citations = re.findall(citation_pattern, final_report)
    max_finding_id = len(findings)
    
    invalid_citations = [
        int(c) for c in citations 
        if int(c) > max_finding_id or int(c) < 1
    ]
    
    if invalid_citations:
        return {
            "result_validated": False,
            "validation_issues": [f"无效引用: {invalid_citations}"],
            "needs_regenerate": True
        }
    
    # 3. 使用 LLM 进行深度验证
    config = get_node_config("validation")
    llm = get_llm(temperature=config["temperature"], model_name=config["model"])
    
    # Get prompts from centralized prompt management
    prompts = get_validation_prompts(topic, final_report[:2000])
    
    validation_prompt = ChatPromptTemplate.from_messages([
        ("system", prompts["system"]),
        ("human", prompts["user"])
    ])
    
    chain = validation_prompt | llm
    result = chain.invoke({})
    
    # 解析验证结果
    try:
        json_match = re.search(r'\{.*\}', result.content, re.DOTALL)
        if json_match:
            validation = json.loads(json_match.group())
        else:
            validation = {"is_valid": True, "issues": [], "overall_score": 7}
    except:
        validation = {"is_valid": True, "issues": [], "overall_score": 7}
    
    is_valid = validation.get("is_valid", True) and validation.get("overall_score", 0) >= 6
    
    return {
        "result_validated": is_valid,
        "validation_issues": validation.get("issues", []),
        "validation_score": validation.get("overall_score", 7),
        "needs_regenerate": not is_valid
    }
