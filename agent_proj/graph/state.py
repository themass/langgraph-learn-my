"""
State definition for the Industry Research Agent.
"""
from typing import List, Optional, TypedDict, Annotated, Union, Dict
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field
import operator

class PlanStep(BaseModel):
    id: str = Field(description="Unique ID of the step")
    description: str = Field(description="Description of what to do")
    dependencies: List[str] = Field(default_factory=list, description="IDs of steps that must be completed first")
    status: str = Field(default="pending", description="pending, running, completed, or failed")
    observation_ref: Optional[List[str]] = Field(default=None, description="References to observation IDs collected in this step")

class Fact(BaseModel):
    """A structured finding with source tracking."""
    content: str
    source_url: str
    step_id: str

class AgentState(TypedDict):
    # --- Global Context ---
    user_id: str
    session_id: str
    topic: str
    
    # --- L1: Plan & Strategy ---
    plan: List[PlanStep]
    current_step_index: int
    
    # --- L2: Execution (ReAct Loop) ---
    # 新增: 记录 Executor 的完整 ReAct 轨迹
    executor_trace: Dict  # {"thoughts": [], "actions": [], "observations": []}
    
    # --- L3: Analysis & Results ---
    # research_findings accumulates facts across ALL tasks
    research_findings: Annotated[List[Fact], operator.add]
    # 新增: 记录 Analyst 的推理步骤  
    analyst_reasoning_steps: List[Dict]
    final_report: str
    
    # --- Progress Check ---
    needs_replan: bool
    progress_assessment: Optional[Dict]
    
    # --- Validation & Quality Gates ---
    input_validated: bool  # 输入是否验证通过
    is_simple_question: bool  # 是否简单问题
    result_validated: bool  # 结果是否验证通过
    validation_issues: List[str]  # 验证发现的问题
    validation_score: Optional[float]  # 质量评分 (0-10)
    needs_regenerate: bool  # 是否需要重新生成
    
    # --- Error Recovery ---
    retry_count: int  # 重试次数
    max_retries: int  # 最大重试次数
    
    # --- Reflection & Uncertainty ---
    reflection_passed: bool  # 反思是否通过
    reflection_issues: List[str]  # 反思发现的问题
    reflection_suggestions: List[str]  # 改进建议
    reasoning_confidence: float  # 推理置信度 (0-1)
    overall_confidence: float  # 整体置信度 (0-1)
    confidence_breakdown: Dict  # 置信度分解
    uncertainty_sources: List[str]  # 不确定性来源
    needs_more_information: bool  # 是否需要更多信息
    uncertainty_handled: bool  # 不确定性是否已处理
    
    # --- Signals & Control Flow ---
    next_node: Optional[str] # For forcing transitions
    error_state: Optional[str] # Traceback or error message for recovery
