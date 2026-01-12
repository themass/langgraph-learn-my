from langgraph.graph import StateGraph, END
from agent_proj.graph.state import AgentState
from agent_proj.graph.nodes.input_validation import input_validation_node
from agent_proj.graph.nodes.planner import planner_node
from agent_proj.graph.nodes.executor import executor_node
from agent_proj.graph.nodes.analyst import analyst_node
from agent_proj.graph.nodes.progress_check import progress_check_node
from agent_proj.graph.nodes.reflection import reflection_node
from agent_proj.graph.nodes.uncertainty_handling import uncertainty_handling_node
from agent_proj.graph.nodes.result_validation import result_validation_node

def decide_next_step(state: AgentState):
    """
    Decide the next step after Progress Check or Planner.
    Routes to: 'planner', 'executor', or 'analyst'
    """
    # 0. Check for errors
    if state.get("error_state"):
        return "end"
    
    # 1. Check if replan is needed
    if state.get("needs_replan", False):
        return "planner"
    
    # 2. Normal routing based on plan progress
    plan = state.get("plan", [])
    idx = state.get("current_step_index", 0)
    
    if not plan:
        return "planner"
        
    if idx < len(plan):
        return "executor"
        
    return "analyst"

def build_graph(checkpointer=None):
    """
    Compile the StateGraph with production-grade quality gates
    """
    workflow = StateGraph(AgentState)
    
    # Add All Nodes
    workflow.add_node("input_validation", input_validation_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("progress_check", progress_check_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("reflection", reflection_node)
    workflow.add_node("uncertainty_handling", uncertainty_handling_node)
    workflow.add_node("result_validation", result_validation_node)
    
    # Entry Point
    workflow.set_entry_point("input_validation")
    
    # Input Validation -> Router
    def after_input_validation(state):
        if state.get("error_state"):
            return "end"
        return "router"
    
    workflow.add_conditional_edges(
        "input_validation",
        after_input_validation,
        {"router": "planner", "end": END}
    )
    
    # Planner -> Router
    workflow.add_conditional_edges(
        "planner",
        decide_next_step,
        {"executor": "executor", "analyst": "analyst", "planner": "planner", "end": END}
    )
    
    # Executor -> Progress Check
    workflow.add_edge("executor", "progress_check")
    
    # Progress Check -> Router
    workflow.add_conditional_edges(
        "progress_check",
        decide_next_step,
        {
            "planner": "planner",
            "executor": "executor",
            "analyst": "analyst", 
            "end": END
        }
    )
    
    # Analyst -> Reflection (新增质量门控)
    workflow.add_edge("analyst", "reflection")
    
    # Reflection -> Analyst (如果反思未通过) or Uncertainty
    def after_reflection(state):
        if not state.get("reflection_passed", True):
            retry_count = state.get("retry_count", 0)
            max_retries = state.get("max_retries", 2)
            if retry_count < max_retries:
                return "analyst"  # 重新推理
        return "uncertainty"
    
    workflow.add_conditional_edges(
        "reflection",
        after_reflection,
        {
            "analyst": "analyst",
            "uncertainty": "uncertainty_handling"
        }
    )
    
    # Uncertainty Handling -> Result Validation
    workflow.add_edge("uncertainty_handling", "result_validation")
    
    # Result Validation -> Router or END
    def after_result_validation(state):
        if state.get("needs_regenerate", False):
            retry_count = state.get("retry_count", 0)
            max_retries = state.get("max_retries", 2)
            if retry_count < max_retries:
                return "analyst"
        return "end"
    
    workflow.add_conditional_edges(
        "result_validation",
        after_result_validation,
        {"analyst": "analyst", "end": END}
    )
    
    return workflow.compile(checkpointer=checkpointer)
