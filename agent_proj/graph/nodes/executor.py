from typing import Dict, List, Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from agent_proj.graph.state import AgentState, Fact
from agent_proj.tools import search_market_data, scrape_web_content, get_financial_metrics
from agent_proj.utils import get_llm
from agent_proj.prompts import get_executor_prompts, get_node_config
from agent_proj.logger import log_node_start, log_node_output, log_node_end, log_tool_call, log_llm_call
import json
import time

# 工具映射
AVAILABLE_TOOLS = {
    "search_market_data": search_market_data,
    "scrape_web_content": scrape_web_content,
    "get_financial_metrics": get_financial_metrics
}

def executor_node(state: AgentState) -> Dict:
    """
    L2 Executor Node: 基于 ReAct 范式执行单个任务
    使用显式的 Think→Act→Observe 循环，不依赖 create_react_agent
    """
    start_time = time.time()
    log_node_start("Executor", state)
    
    plan = state.get("plan", [])
    idx = state.get("current_step_index", 0)
    
    if idx >= len(plan):
        log_node_end("Executor", time.time() - start_time)
        return {"next_node": "analyst"}
        
    current_step = plan[idx]
    current_step.status = "running"
    
    print(f"🎯 执行任务: {current_step.description}")
    
    # 初始化 ReAct 轨迹记录
    thoughts = []
    actions = []
    observations = []
    
    MAX_STEPS = 15  # 最大推理循环次数，避免无限循环
    config = get_node_config("executor")
    llm = get_llm(temperature=config["temperature"], model_name=config["model"])
    
    print(f"\n⚙️  配置信息:")
    print(f"   • 最大推理循环: {MAX_STEPS} 次")
    print(f"   • LLM 温度: {config['temperature']}")
    print(f"   • LLM 模型: {config['model']}")
    
    # ReAct Loop
    for step_num in range(MAX_STEPS):
        print(f"\n{'='*60}")
        print(f"🔄 ReAct Cycle {step_num + 1}/{MAX_STEPS}")
        print(f"{'='*60}")
        
        # 1. THINK: 分析当前状态，决定下一步行动
        # 构建已有观察结果文本
        observations_text = chr(10).join([f"[{i+1}] {obs}" for i, obs in enumerate(observations)]) if observations else "无"
        
        # Get prompts from centralized prompt management
        prompts = get_executor_prompts(current_step.description, observations_text)
        
        log_llm_call("Executor", "think", len(prompts["system"]) + len(prompts["user"]))
        
        think_prompt = ChatPromptTemplate.from_messages([
            ("system", prompts["system"]),
            ("human", prompts["user"])
        ])
        
        chain = think_prompt | llm
        think_result = chain.invoke({})
        
        # 解析 Thought
        try:
            import re
            json_match = re.search(r'\{.*\}', think_result.content, re.DOTALL)
            if json_match:
                decision = json.loads(json_match.group())
            else:
                decision = {"thought": think_result.content, "action": "finish", "action_input": ""}
        except:
            decision = {"thought": think_result.content, "action": "finish", "action_input": ""}
        
        thought = decision.get("thought", "")
        action = decision.get("action", "finish")
        action_input = decision.get("action_input", "")
        
        print(f"\n💭 【思考过程】:")
        print(f"   {thought}")
        print(f"\n⚡ 【决策】:")
        print(f"   • 动作: {action}")
        print(f"   • 输入: {action_input if action_input else '(无)'}")
        
        thoughts.append(thought)
        
        # 2. ACT & OBSERVE: 执行工具或结束
        if action == "finish":
            observation = "任务完成"
            observations.append(observation)
            print(f"\n✅ 【观察结果】:")
            print(f"   {observation}")
            break
        
        if action not in AVAILABLE_TOOLS:
            observation = f"错误: 未知工具 '{action}'"
            observations.append(observation)
            actions.append({"action": action, "input": action_input, "success": False})
            print(f"\n❌ 【观察结果】:")
            print(f"   {observation}")
            continue
        
        # 执行工具
        print(f"\n🔧 【工具调用】:")
        print(f"   • 工具名称: {action}")
        print(f"   • 输入参数: {action_input}")
        
        try:
            tool = AVAILABLE_TOOLS[action]
            if action == "search_market_data":
                observation = tool.invoke({"query": action_input})
            elif action == "scrape_web_content":
                observation = tool.invoke({"url": action_input})
            elif action == "get_financial_metrics":
                observation = tool.invoke({"ticker": action_input})
            else:
                observation = str(tool.invoke({}))
            
            # 记录详细的工具调用日志
            obs_preview = str(observation)[:200] + "..." if len(str(observation)) > 200 else str(observation)
            log_tool_call("Executor", action, action_input, obs_preview)
            
            observations.append(observation)
            actions.append({"action": action, "input": action_input, "success": True})
            
            print(f"\n📊 【观察结果】:")
            print(f"   {obs_preview}")
            
        except Exception as e:
            observation = f"工具执行错误: {str(e)}"
            observations.append(observation)
            actions.append({"action": action, "input": action_input, "success": False, "error": str(e)})
            
            print(f"\n❌ 【观察结果】:")
            print(f"   {observation}")
    
    # 3. 汇总为 Fact
    facts = []
    for i, obs in enumerate(observations, 1):
        if obs != "任务完成" and "错误" not in str(obs):
            # 确保 obs 是字符串
            obs_str = str(obs) if not isinstance(obs, str) else obs
            facts.append(Fact(
                content=obs_str[:500],  # 截断过长内容
                source_url="tool-generated",  # 工具生成的数据
                step_id=current_step.id
            ))
    
    # 4. 显示执行总结
    print(f"\n{'='*80}")
    print(f"📊 【执行总结】")
    print(f"{'='*80}")
    print(f"   • 推理循环次数: {len(thoughts)} 次")
    print(f"   • 工具调用次数: {len(actions)} 次")
    print(f"   • 成功调用: {sum(1 for a in actions if a.get('success', False))} 次")
    print(f"   • 失败调用: {sum(1 for a in actions if not a.get('success', True))} 次")
    print(f"   • 收集到的证据: {len(facts)} 条")
    print(f"{'='*80}\n")
    
    # 5. 更新状态
    current_step.status = "completed"
    
    output = {
        "current_step_index": idx + 1,
        "research_findings": facts,
        "executor_trace": {
            "thoughts": thoughts,
            "actions": actions,
            "observations": observations
        }
    }
    
    log_node_output("Executor", {
        "facts_collected": len(facts),
        "cycles_used": len(thoughts),
        "tools_called": len(actions),
        "step_status": "completed"
    })
    log_node_end("Executor", time.time() - start_time)
    
    return output