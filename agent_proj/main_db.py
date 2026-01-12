"""
ProAgent Database Launch Script
Uses MySQL for persistent state management.
"""
import asyncio
import os
import sys
import uuid
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_proj.graph.workflow import build_graph
from agent_proj.graph.state import AgentState
from agent_proj.db_checkpointer import get_checkpointer

load_dotenv()

async def main():
    print("=" * 80)
    print("ProAgent with MySQL Persistence")
    print("=" * 80)
    
    # 1. 验证配置
    print(f"\n[1] Validating Database Configuration...")
    try:
        from agent_proj.db_checkpointer import build_database_url
        db_url = build_database_url()
        print("✅ Configuration Loaded")
    except ValueError as e:
        print(f"❌ Configuration Error:\n{str(e)}")
        print("\n💡 请在 .env 文件中配置以下任一方式：")
        print("\n【推荐】方式 1: 分开配置（自动处理密码特殊字符）")
        print("  DB_USER=your_username")
        print("  DB_PASSWORD=your_p@ssw0rd!")
        print("  DB_HOST=localhost")
        print("  DB_PORT=3306")
        print("  DB_NAME=proagent")
        print("\n方式 2: 完整 URL（密码无特殊字符时）")
        print("  DATABASE_URL=mysql+aiomysql://user:pass@host:port/dbname")
        return

    print(f"\n[2] Connecting to Database...")
    
    # 2. 启动 Checkpointer 上下文
    try:
        async with get_checkpointer() as checkpointer:
            print("✅ DB Connected & Tables checked")
            
            # 3. 编译图 (带 checkpointer)
            print("\n[3] Compiling Graph with Persistence...")
            graph = build_graph(checkpointer=checkpointer)
            print("✅ Graph Compiled")
            
            # 4. 初始化配置 (Thread ID 用于持久化)
            thread_id = str(uuid.uuid4())
            config = {"configurable": {"thread_id": thread_id}}
            print(f"\n✅ Session ID (thread_id): {thread_id}")
            print("   (Use this ID to resume or query status later)")
            
            # 5. 初始化状态
            print("\n[4] Initializing State...")
            initial_state = {
                "user_id": "test_user_db",
                "session_id": thread_id,
                "topic": "2024年低空经济市场分析",
                "plan": [],
                "current_step_index": 0,
                "research_findings": [],
                "max_retries": 2
            }

            # 6. 执行工作流
            print("\n[5] Starting Workflow Execution...")
            print("-" * 80)
            
            # 使用 astream 或 ainvoke (因为 checkpointer 是 async 的，通常建议 run in async context)
            # Normal invoke might work if checkpointer handles sync via loop, but async is safer.
            
            final_result = None
            async for event in graph.astream(initial_state, config=config, stream_mode="values"):
                # 打印当前节点产生的最新状态摘要
                if event.get("final_report"):
                    final_result = event
                    print("\n>>> Report Generated!")
                elif event.get("plan") and len(event["plan"]) > 0:
                     print(f"   -> Current Step: {event.get('current_step_index')}/{len(event['plan'])}")
            
            print("\n" + "=" * 80)
            print("执行完成！")
            
            if final_result:
                print("\n【最终报告】")
                print("-" * 80)
                print(final_result.get("final_report")[:500] + "...") # Preview
            
            # 验证持久化
            print("\n[6] Verifying Persistence...")
            # 从数据库重新读取状态
            saved_state = await graph.aget_state(config)
            print(f"✅ Retrieved State from DB: Step Index = {saved_state.values.get('current_step_index')}")
            
    except Exception as e:
        print(f"\n❌ Execution Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
