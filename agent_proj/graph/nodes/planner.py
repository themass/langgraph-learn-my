from typing import Dict, List
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from agent_proj.graph.state import AgentState, PlanStep
from agent_proj.utils import get_llm
from agent_proj.prompts import get_planner_prompts, get_node_config
from agent_proj.logger import log_node_start, log_node_output, log_node_end, log_llm_call
from pydantic import BaseModel, Field
import json
import re
import time

# Output Schema for the Planner
class PlannerOutput(BaseModel):
    plan: List[PlanStep] = Field(description="List of steps to complete the research")
    rationale: str = Field(description="Reasoning behind the plan structure")

def planner_node(state: AgentState) -> Dict:
    """
    L1 Planner Node: Generates a research plan based on the topic.
    """
    start_time = time.time()
    log_node_start("Planner", state)
    
    topic = state.get("topic")
    plan = state.get("plan", [])
    
    # 显示节点输入信息
    print(f"\n📥 【节点输入】:")
    print(f"   • 研究主题: {topic}")
    print(f"   • 现有计划: {'是' if len(plan) > 0 else '否'} ({len(plan)} 个步骤)")
    
    # Check if we are replanning (error recovery or refinement)
    is_replanning = len(plan) > 0
    
    # Get node configuration
    config = get_node_config("planner")
    llm = get_llm(temperature=config["temperature"], model_name=config["model"])
    
    print(f"\n⚙️  【配置信息】:")
    print(f"   • LLM 温度: {config['temperature']}")
    print(f"   • LLM 模型: {config['model']}")
    print(f"   • 是否重新规划: {'是' if is_replanning else '否'}")
    
    if not is_replanning:
        # Get prompts from centralized prompt management
        prompts = get_planner_prompts(topic)
        system_prompt = prompts["system"]
        user_msg = prompts["user"]
    else:
        # Replanning
        # This basic implementation just keeps the old plan for now 
        # but in a full version it would look at 'error_state' and adjust.
        # For this turn, let's assume valid plan exists or we just refresh it.
        # To keep it simple for the MVP, we only plan if plan is empty.
        return {} # No op if plan exists

    # Try structured output first
    try:
        log_llm_call("Planner", "system+user", len(system_prompt) + len(user_msg))
        
        # Structural binding
        planner = llm.with_structured_output(PlannerOutput)
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_msg)
        ]
        
        result: PlannerOutput = planner.invoke(messages)
        
        log_llm_call("Planner", "response", 0, len(str(result)))
        
    except Exception as e:
        # Fallback: Parse JSON manually if structured output fails
        print(f"⚠️ Structured output failed: {e}")
        print("   Falling back to manual JSON parsing...")
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_msg)
        ]
        
        response = llm.invoke(messages)
        
        # Extract JSON from response
        try:
            # Find JSON object in the response
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed_data = json.loads(json_str)
                
                # Manually construct PlannerOutput
                plan_steps = [
                    PlanStep(
                        id=str(i+1),
                        description=step.get("description", ""),
                        status="pending",
                        dependencies=step.get("dependencies", [])
                    )
                    for i, step in enumerate(parsed_data.get("plan", []))
                ]
                
                result = PlannerOutput(
                    plan=plan_steps,
                    rationale=parsed_data.get("rationale", "Generated via fallback parsing")
                )
            else:
                # Last resort: Create a simple default plan
                print("⚠️ Could not parse JSON, using default plan")
                result = PlannerOutput(
                    plan=[
                        PlanStep(id="1", description=f"研究 {topic} 的市场规模和定义", status="pending"),
                        PlanStep(id="2", description=f"分析 {topic} 的竞争格局", status="pending"),
                        PlanStep(id="3", description=f"识别 {topic} 的关键趋势和驱动因素", status="pending"),
                    ],
                    rationale="Default plan due to parsing failure"
                )
        except Exception as parse_error:
            print(f"⚠️ Fallback parsing also failed: {parse_error}")
            # Create default plan
            result = PlannerOutput(
                plan=[
                    PlanStep(id="1", description=f"研究 {topic} 的基本信息", status="pending"),
                    PlanStep(id="2", description=f"分析 {topic} 的市场状况", status="pending"),
                    PlanStep(id="3", description=f"总结 {topic} 的发展趋势", status="pending"),
                ],
                rationale="Default plan due to errors"
            )
    
    # Initialize the plan
    output = {
        "plan": result.plan,
        "current_step_index": 0,
        "research_findings": []  # Reset findings
    }
    
    # 显示生成的计划详情
    print(f"\n{'='*80}")
    print(f"📋 【生成的研究计划】")
    print(f"{'='*80}")
    print(f"   prompt:\n {messages}")
    print(f"   output:\n {result.model_dump_json(indent=2, ensure_ascii=False)}")
    for i, step in enumerate(result.plan, 1):
        print(f"   步骤 {i}: {step.description}")
        print(f"      • ID: {step.id}")
        print(f"      • 状态: {step.status}")
        if step.dependencies:
            print(f"      • 依赖: {', '.join(step.dependencies)}")
    print(f"\n   规划理由: {result.rationale[:200]}{'...' if len(result.rationale) > 200 else ''}")
    print(f"{'='*80}\n")
    
    log_node_output("Planner", {
        "plan_count": len(result.plan),
        "plan_steps": [step.description for step in result.plan],
        "rationale": result.rationale[:200]
    })
    log_node_end("Planner", time.time() - start_time)
    
    return output

