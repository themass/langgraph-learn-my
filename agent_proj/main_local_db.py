"""
ProAgent Local Database Launch Script
Uses SQLite for local persistent state management.
No setup required - creates 'checkpoints.sqlite' in current directory.

Note: This version includes a compatibility fix for aiosqlite.Connection.is_alive()
"""
import asyncio
import os
import sys
import uuid
import aiosqlite
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================================================
# Compatibility Fix for aiosqlite
# ============================================================================
# aiosqlite 0.22.1 的 Connection 对象没有 is_alive() 方法
# 但 LangGraph AsyncSqliteSaver 需要此方法
# 这里添加一个兼容性补丁

if not hasattr(aiosqlite.Connection, 'is_alive'):
    def is_alive(self):
        """检查连接是否存活
        
        对于 aiosqlite.Connection，我们需要检查：
        1. 连接对象已经初始化（_connection 属性存在）
        2. 内部线程已经启动（_running 为 True）
        """
        try:
            # 检查连接是否已初始化且线程正在运行
            return (hasattr(self, '_running') and 
                    self._running and 
                    hasattr(self, '_connection') and 
                    self._connection is not None)
        except Exception as e:
            # 如果检查过程中出错，认为连接不可用
            return False
    
    # 动态添加方法到 aiosqlite.Connection 类
    aiosqlite.Connection.is_alive = is_alive
    print("✅ Applied compatibility patch for aiosqlite.Connection.is_alive()")

# ============================================================================

from agent_proj.graph.workflow import build_graph
from agent_proj.logger import log_workflow_event, log_state_summary, Colors
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

load_dotenv()

async def main():
    print("=" * 80)
    print("ProAgent with Local SQLite Persistence")
    print("=" * 80)
    
    db_path = "checkpoints.sqlite"
    print(f"\n[1] Using Local Database: {db_path}")
    
    # 创建并等待 aiosqlite 连接完全初始化
    # 注意：aiosqlite.connect() 返回一个 Connection 对象，需要 await 来完成初始化
    conn_awaitable = aiosqlite.connect(db_path)
    conn = await conn_awaitable  # 完成连接初始化
    
    # 创建 AsyncSqliteSaver
    checkpointer = AsyncSqliteSaver(conn)
    
    try:
        # 初始化表结构
        await checkpointer.setup()
        print("✅ DB Connected & Tables Initialized")
        
        # 3. 编译图 (带 checkpointer)
        print("\n[2] Compiling Graph with Persistence...")
        graph = build_graph(checkpointer=checkpointer)
        print("✅ Graph Compiled")
        
        # 4. 初始化配置
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        print(f"\n✅ Session ID (thread_id): {thread_id}")
        
        # 5. 初始化状态
        print("\n[3] Initializing State...")
        initial_state = {
            "user_id": "test_user_local",
            "session_id": thread_id,
            "topic": "2024年低空经济市场分析",
            "plan": [],
            "current_step_index": 0,
            "research_findings": [],
            "max_retries": 2
        }

        # 6. 执行工作流
        print("\n[4] Starting Workflow Execution...")
        print("=" * 80)
        
        final_result = None
        last_step_idx = -1
        
        async for event in graph.astream(initial_state, config=config, stream_mode="values"):
            current_step_idx = event.get('current_step_index', 0)
            plan = event.get('plan', [])
            findings = event.get('research_findings', [])
            
            # 显示详细的执行状态
            if plan and len(plan) > 0:
                # 只在步骤变化时显示
                if current_step_idx != last_step_idx:
                    print(f"\n📍 Step {current_step_idx}/{len(plan)}")
                    
                    # 显示当前步骤信息
                    if current_step_idx > 0 and current_step_idx <= len(plan):
                        current_task = plan[current_step_idx - 1]
                        print(f"   ✓ 已完成: {current_task.description}")
                        print(f"   ✓ 状态: {current_task.status}")
                    
                    # 显示下一步骤
                    if current_step_idx < len(plan):
                        next_task = plan[current_step_idx]
                        print(f"   ▶ 下一步: {next_task.description}")
                    
                    # 显示研究发现数量
                    if findings:
                        print(f"   📊 已收集证据: {len(findings)} 条")
                    
                    last_step_idx = current_step_idx
            
            # 显示报告生成
            if event.get("final_report"):
                final_result = event
                report = event["final_report"]
                print(f"\n{'='*80}")
                print("✅ 研究报告生成完成！")
                print(f"{'='*80}")
                print(f"📄 报告长度: {len(report)} 字符")
                print(f"📊 证据数量: {len(findings)} 条")
                
                # 显示报告摘要
                lines = report.split('\n')
                print(f"\n📋 报告摘要 (前5行):")
                for line in lines[:5]:
                    if line.strip():
                        print(f"   {line}")
                
            # 显示质量验证结果
            if event.get("result_validated") is not None:
                is_valid = event.get("result_validated")
                score = event.get("validation_score", 0)
                if is_valid:
                    print(f"\n✅ 质量验证: 通过 (评分: {score}/10)")
                else:
                    print(f"\n⚠️  质量验证: 未通过 (评分: {score}/10)")
                    issues = event.get("validation_issues", [])
                    if issues:
                        print(f"   问题: {', '.join(issues)}")
            
            # 显示不确定性评估
            if event.get("overall_confidence") is not None:
                confidence = event.get("overall_confidence", 0)
                emoji = "🟢" if confidence > 0.7 else "🟡" if confidence > 0.5 else "🔴"
                print(f"\n{emoji} 置信度评估: {confidence:.2%}")
                
                uncertainties = event.get("uncertainty_sources", [])
                if uncertainties:
                    print(f"   不确定性来源: {', '.join(uncertainties[:3])}")
            
            # 显示反思结果
            if event.get("reflection_passed") is not None:
                passed = event.get("reflection_passed")
                if not passed:
                    print(f"\n🔍 推理质量检查: 发现问题")
                    issues = event.get("reflection_issues", [])
                    if issues:
                        print(f"   问题: {', '.join(issues[:2])}")
                else:
                    print(f"\n✅ 推理质量检查: 通过")
        
        print("\n" + "=" * 80)
        print("执行完成！")
        
        if final_result:
            # 显示状态摘要
            log_state_summary(final_result)
            
            print(f"\n{Colors.HEADER}【最终报告预览】{Colors.ENDC}")
            print(f"{Colors.HEADER}{'-' * 80}{Colors.ENDC}")
            report_preview = final_result.get("final_report", "")[:800]
            print(report_preview)
            if len(final_result.get("final_report", "")) > 800:
                print(f"\n{Colors.WARNING}... (报告总长度: {len(final_result['final_report'])} 字符){Colors.ENDC}")
            print(f"{Colors.HEADER}{'-' * 80}{Colors.ENDC}") 
        
        # 验证持久化
        print("\n[5] Verifying Persistence...")
        saved_state = await graph.aget_state(config)
        print(f"✅ Retrieved State from DB: Step Index = {saved_state.values.get('current_step_index')}")
        print(f"✅ Data persisted to: {db_path}")
        
    finally:
        # 关闭数据库连接
        await conn.close()
        print("\n✅ Database connection closed")

if __name__ == "__main__":
    asyncio.run(main())
