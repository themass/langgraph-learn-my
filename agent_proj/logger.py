"""
ProAgent Logging System
=======================

统一的日志系统，用于记录节点执行的详细信息
"""

import json
from typing import Any, Dict
from datetime import datetime


class Colors:
    """终端颜色代码"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def format_value(value: Any, max_length: int = 200) -> str:
    """格式化值用于显示
    
    Args:
        value: 要格式化的值
        max_length: 最大显示长度
        
    Returns:
        格式化后的字符串
    """
    if value is None:
        return "None"
    
    if isinstance(value, (list, tuple)):
        if len(value) == 0:
            return "[]"
        items_str = ", ".join([format_value(item, max_length=50) for item in value[:3]])
        suffix = f", ... (共{len(value)}项)" if len(value) > 3 else ""
        return f"[{items_str}{suffix}]"
    
    if isinstance(value, dict):
        if len(value) == 0:
            return "{}"
        # 只显示前3个键值对
        items = list(value.items())[:3]
        items_str = ", ".join([f'"{k}": {format_value(v, max_length=50)}' for k, v in items])
        suffix = f", ... (共{len(value)}个字段)" if len(value) > 3 else ""
        return f"{{{items_str}{suffix}}}"
    
    value_str = str(value)
    if len(value_str) > max_length:
        return value_str[:max_length] + "..."
    return value_str


def log_node_start(node_name: str, state: Dict[str, Any]):
    """记录节点开始执行
    
    Args:
        node_name: 节点名称
        state: 当前状态
    """
    print(f"\n{Colors.OKBLUE}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKBLUE}▶ 节点开始: {node_name}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{'='*80}{Colors.ENDC}")
    
    # 提取关键状态信息
    key_info = {
        "topic": state.get("topic", "N/A"),
        "current_step": state.get("current_step_index", 0),
        "total_steps": len(state.get("plan", [])),
        "findings_count": len(state.get("research_findings", [])),
    }
    
    print(f"{Colors.OKCYAN}⏱  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}📊 当前状态:{Colors.ENDC}")
    for key, value in key_info.items():
        print(f"   • {key}: {Colors.BOLD}{format_value(value)}{Colors.ENDC}")
    
    # 如果有当前执行步骤，显示详情
    if state.get("plan") and state.get("current_step_index", 0) < len(state["plan"]):
        current_step = state["plan"][state["current_step_index"]]
        print(f"\n{Colors.OKCYAN}📋 当前执行步骤:{Colors.ENDC}")
        # PlanStep 是 Pydantic 模型，使用属性访问而不是 .get()
        print(f"   • ID: {getattr(current_step, 'id', 'N/A')}")
        print(f"   • 描述: {getattr(current_step, 'description', 'N/A')}")
        print(f"   • 状态: {getattr(current_step, 'status', 'N/A')}")


def log_node_input(node_name: str, input_data: Dict[str, Any]):
    """记录节点输入详情
    
    Args:
        node_name: 节点名称
        input_data: 输入数据
    """
    print(f"\n{Colors.OKGREEN}📥 节点输入 ({node_name}):{Colors.ENDC}")
    
    if not input_data:
        print(f"   {Colors.WARNING}(无输入数据){Colors.ENDC}")
        return
    
    for key, value in input_data.items():
        print(f"   • {key}: {format_value(value, max_length=150)}")


def log_node_output(node_name: str, output_data: Dict[str, Any]):
    """记录节点输出详情
    
    Args:
        node_name: 节点名称
        output_data: 输出数据
    """
    print(f"\n{Colors.OKGREEN}📤 节点输出 ({node_name}):{Colors.ENDC}")
    
    if not output_data:
        print(f"   {Colors.WARNING}(无输出数据){Colors.ENDC}")
        return
    
    for key, value in output_data.items():
        if key in ["final_report", "analyst_reasoning_steps"] and value:
            # 特殊处理长文本字段
            value_preview = format_value(value, max_length=200)
            print(f"   • {key}: {value_preview}")
        else:
            print(f"   • {key}: {format_value(value, max_length=150)}")


def log_node_end(node_name: str, execution_time: float = None):
    """记录节点执行结束
    
    Args:
        node_name: 节点名称
        execution_time: 执行时间（秒）
    """
    time_str = f" ({execution_time:.2f}s)" if execution_time else ""
    print(f"\n{Colors.OKGREEN}✅ 节点完成: {node_name}{time_str}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{'='*80}{Colors.ENDC}\n")


def log_llm_call(node_name: str, prompt_type: str, prompt_length: int, response_length: int = None):
    """记录 LLM 调用
    
    Args:
        node_name: 节点名称
        prompt_type: Prompt 类型 (system/user)
        prompt_length: Prompt 长度
        response_length: 响应长度
    """
    response_str = f", 响应: {response_length} 字符" if response_length else ""
    print(f"{Colors.OKCYAN}🤖 LLM 调用 ({node_name}): {prompt_type} Prompt ({prompt_length} 字符){response_str}{Colors.ENDC}")


def log_tool_call(node_name: str, tool_name: str, tool_input: Any, result_preview: str = None):
    """记录工具调用
    
    Args:
        node_name: 节点名称
        tool_name: 工具名称
        tool_input: 工具输入
        result_preview: 结果预览
    """
    print(f"{Colors.WARNING}🔧 工具调用 ({node_name}):{Colors.ENDC}")
    print(f"   • 工具: {tool_name}")
    print(f"   • 输入: {format_value(tool_input, max_length=100)}")
    if result_preview:
        print(f"   • 结果: {result_preview}")


def log_error(node_name: str, error: Exception):
    """记录错误
    
    Args:
        node_name: 节点名称
        error: 异常对象
    """
    print(f"\n{Colors.FAIL}❌ 错误发生 ({node_name}):{Colors.ENDC}")
    print(f"   {Colors.FAIL}• 类型: {type(error).__name__}{Colors.ENDC}")
    print(f"   {Colors.FAIL}• 信息: {str(error)}{Colors.ENDC}")


def log_decision(node_name: str, decision: str, reason: str = None):
    """记录决策点
    
    Args:
        node_name: 节点名称
        decision: 决策结果
        reason: 决策原因
    """
    print(f"\n{Colors.WARNING}🔀 决策点 ({node_name}):{Colors.ENDC}")
    print(f"   • 决策: {Colors.BOLD}{decision}{Colors.ENDC}")
    if reason:
        print(f"   • 原因: {reason}")


def log_workflow_event(event_type: str, details: Dict[str, Any]):
    """记录工作流事件
    
    Args:
        event_type: 事件类型
        details: 事件详情
    """
    icons = {
        "plan_created": "📝",
        "step_completed": "✅",
        "report_generated": "📄",
        "validation_passed": "✓",
        "validation_failed": "✗",
        "retry": "🔄"
    }
    
    icon = icons.get(event_type, "ℹ")
    print(f"{Colors.OKCYAN}{icon} 工作流事件: {event_type}{Colors.ENDC}")
    
    for key, value in details.items():
        print(f"   • {key}: {format_value(value)}")


def log_state_summary(state: Dict[str, Any]):
    """记录状态摘要
    
    Args:
        state: 当前状态
    """
    print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}📊 状态摘要{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
    
    summary = {
        "主题": state.get("topic", "N/A"),
        "当前步骤": f"{state.get('current_step_index', 0)}/{len(state.get('plan', []))}",
        "研究发现数量": len(state.get("research_findings", [])),
        "推理步骤数量": len(state.get("analyst_reasoning_steps", [])),
        "是否有报告": "是" if state.get("final_report") else "否",
        "报告长度": len(state.get("final_report", "")) if state.get("final_report") else 0,
        "重试次数": state.get("retry_count", 0),
    }
    
    for key, value in summary.items():
        print(f"   • {key}: {Colors.BOLD}{value}{Colors.ENDC}")
    
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
