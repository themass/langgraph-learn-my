"""
ProAgent 启动脚本
用于测试完整的工作流
"""
import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_proj.graph.workflow import build_graph
from agent_proj.graph.state import AgentState

# 加载环境变量
load_dotenv()

def test_proagent():
    """测试 ProAgent 完整流程"""
    
    print("=" * 80)
    print("ProAgent 启动测试")
    print("=" * 80)
    
    # 编译图
    print("\n[1] 编译 LangGraph...")
    graph = build_graph()
    print("✅ 图编译成功")
    
    # 初始化状态
    print("\n[2] 初始化状态...")
    initial_state: AgentState = {
        # Global Context
        "user_id": "test_user",
        "session_id": "test_session_001",
        "topic": "2024年低空经济市场分析",
        
        # L1 Plan
        "plan": [],
        "current_step_index": 0,
        
        # L2 Execution
        "executor_trace": {},
        
        # L3 Analysis
        "research_findings": [],
        "analyst_reasoning_steps": [],
        "final_report": "",
        
        # Progress Check
        "needs_replan": False,
        "progress_assessment": None,
        
        # Validation & Quality Gates
        "input_validated": False,
        "is_simple_question": False,
        "result_validated": False,
        "validation_issues": [],
        "validation_score": None,
        "needs_regenerate": False,
        
        # Error Recovery
        "retry_count": 0,
        "max_retries": 2,
        
        # Reflection & Uncertainty
        "reflection_passed": True,
        "reflection_issues": [],
        "reflection_suggestions": [],
        "reasoning_confidence": 0.8,
        "overall_confidence": 0.8,
        "confidence_breakdown": {},
        "uncertainty_sources": [],
        "needs_more_information": False,
        "uncertainty_handled": False,
        
        # Control Flow
        "next_node": None,
        "error_state": None
    }
    print("✅ 状态初始化完成")
    
    # 执行图
    print("\n[3] 开始执行工作流...")
    print("-" * 80)
    
    try:
        result = graph.invoke(initial_state)
        
        print("\n" + "=" * 80)
        print("执行完成！")
        print("=" * 80)
        
        # 输出结果
        print("\n【最终报告】")
        print("-" * 80)
        print(result.get("final_report", "未生成报告"))
        
        print("\n【质量指标】")
        print(f"- 整体置信度: {result.get('overall_confidence', 0):.2f}")
        print(f"- 推理置信度: {result.get('reasoning_confidence', 0):.2f}")
        print(f"- 验证评分: {result.get('validation_score', 0):.1f}/10")
        print(f"- 重试次数: {result.get('retry_count', 0)}/{result.get('max_retries', 2)}")
        
        print("\n【执行统计】")
        print(f"- 研究发现数量: {len(result.get('research_findings', []))}")
        print(f"- 推理步骤数量: {len(result.get('analyst_reasoning_steps', []))}")
        print(f"- 执行计划步骤: {len(result.get('plan', []))}")
        
        if result.get("validation_issues"):
            print("\n【验证问题】")
            for issue in result["validation_issues"]:
                print(f"- {issue}")
        
        if result.get("uncertainty_sources"):
            print("\n【不确定性来源】")
            for source in result["uncertainty_sources"]:
                print(f"- {source}")
        
    except Exception as e:
        print(f"\n❌ 执行失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_proagent()
