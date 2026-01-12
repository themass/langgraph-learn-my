from dataclasses import dataclass
from typing import Literal

from langchain.chat_models import init_chat_model
from langchain_core.tools import tool

from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState
from langgraph.runtime import Runtime
from langchain_openai import ChatOpenAI
from openai import OpenAI

@dataclass
class CustomContext:
    tools: list[Literal["weather", "compass"]]


@tool
def weather() -> str:
    """Returns the current weather conditions."""
    return "It's nice and sunny."


@tool
def compass() -> str:
    """Returns the direction the user is facing."""
    return "North"

# model = init_chat_model(model="ollama")
OLLAMA_BASE_URL = "http://127.0.0.1:11434"
MODEL_NAME = "llama3:latest"

# 创建Ollama LLM实例，连接到指定服务器上的特定模型
# base_url: Ollama服务器地址
# model: 使用的模型名称
# temperature: 控制输出的随机性，值越高回复越多样化
# model = OpenAI(
#     base_url=f"{OLLAMA_BASE_URL}/v1",  # Ollama的OpenAI兼容端点
#     api_key="ollama",  # Ollama不需要真实API key，随意填写即可
# )
model = ChatOpenAI(
    base_url=f"{OLLAMA_BASE_URL}/v1",  # Ollama的OpenAI兼容端点
    api_key="ollama",  # 占位符，Ollama无需真实API key
    model=MODEL_NAME,  # 显式指定模型名称（关键）
    temperature=0  # 控制随机性
)
def configure_model(state: AgentState, runtime: Runtime[CustomContext]):
    """Configure the model with tools based on runtime context."""
    selected_tools = [
        tool
        for tool in [weather, compass]
        if tool.name in runtime.context.tools
    ]
    return model.bind_tools(selected_tools)


agent = create_react_agent(
    # Dynamically configure the model with tools based on runtime context
    configure_model,
    # Initialize with all tools available
    tools=[weather, compass]
)

output = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Who are you and what tools do you have access to?",
            }
        ]
    },
    context=CustomContext(tools=["weather"]),  # Only enable the weather tool
)

print(output["messages"][-1].text())