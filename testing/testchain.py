import os
from typing import Dict, List, Optional
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from datetime import datetime

# 初始化LLM (使用本地Ollama)
llm = OllamaLLM(
    model="llama3",  # 确保已下载此模型: ollama pull llama3
    temperature=0.7
)

# 节点1: 生成诗人基本信息和简介
def generate_poet_info(state: Dict) -> Dict:
    print("=== 生成诗人基本信息 ===")

    prompt = PromptTemplate(
        input_variables=["poet_name"],
        template="""请提供诗人{poet_name}的基本信息和简介，包括：
1. 生卒年份
2. 朝代
3. 主要身份和称号
4. 诗歌风格特点
5. 文学史上的地位和影响

请用简洁明了的语言回答，不超过300字。
"""
    )

    chain = prompt | llm | StrOutputParser()
    poet_info = chain.invoke({"poet_name": state["poet_name"]})

    return {**state, "poet_info": poet_info}

# 节点2: 生成诗人所有诗词和创作时间及背景
def generate_poems_with_context(state: Dict) -> Dict:
    print("\n=== 生成诗词及创作背景 ===")

    prompt = PromptTemplate(
        input_variables=["poet_name", "poet_info"],
        template="""基于以下{poet_name}的基本信息：
{poet_info}

请列出{poet_name}的主要诗词作品，至少10首。每首诗需要包含：
1. 诗词标题
2. 创作年份（尽可能准确，不确定时可标注大致时期）
3. 创作背景（包括当时的历史背景、诗人处境、创作动机等）
4. 诗词全文

请按创作时间顺序排列，格式清晰。
"""
    )

    chain = prompt | llm | StrOutputParser()
    poems_with_context = chain.invoke({
        "poet_name": state["poet_name"],
        "poet_info": state["poet_info"]
    })

    # 简单解析出诗词标题列表，供下一节点使用
    poems = []
    for line in poems_with_context.split('\n'):
        if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
            title = line.split('.', 1)[1].strip().split('：', 1)[0].strip()
            poems.append(title)

    return {**state, "poems_with_context": poems_with_context, "poem_titles": poems}

# 节点3: 针对每首诗词生成解析
def generate_poem_analyses(state: Dict) -> Dict:
    print("\n=== 生成诗词解析 ===")

    all_analyses = []
    for title in state["poem_titles"][:5]:  # 为了演示，只解析前5首
        prompt = PromptTemplate(
            input_variables=["poet_name", "title", "poems_with_context"],
            template="""请解析{poet_name}的《{title}》，基于以下背景信息：
{poems_with_context}

解析应包括：
1. 主题思想和情感表达
2. 艺术特色和修辞手法
3. 名句赏析
4. 这首诗在诗人创作生涯中的地位

请用生动易懂的语言，避免过于学术化的表述。
"""
        )

        chain = prompt | llm | StrOutputParser()
        analysis = chain.invoke({
            "poet_name": state["poet_name"],
            "title": title,
            "poems_with_context": state["poems_with_context"]
        })

        all_analyses.append(f"### 《{title}》解析\n{analysis}")

    return {**state, "poem_analyses": "\n\n".join(all_analyses)}

# 创建工作流
def create_poet_workflow():
    workflow = StateGraph(Dict)

    # 添加节点
    workflow.add_node("generate_poet_info", generate_poet_info)
    workflow.add_node("generate_poems_with_context", generate_poems_with_context)
    workflow.add_node("generate_poem_analyses", generate_poem_analyses)

    # 定义流程
    workflow.add_edge("generate_poet_info", "generate_poems_with_context")
    workflow.add_edge("generate_poems_with_context", "generate_poem_analyses")
    workflow.add_edge("generate_poem_analyses", END)

    # 设置入口点
    workflow.set_entry_point("generate_poet_info")

    return workflow.compile()

if __name__ == "__main__":
    # 创建并运行工作流
    app = create_poet_workflow()

    # 输入参数 - 可以换成其他诗人，如"杜甫"、"白居易"等
    poet_name = "李白"
    print(f"开始分析诗人: {poet_name}\n")

    # 运行工作流
    result = app.invoke({"poet_name": poet_name})

    # 输出结果
    print("\n\n===== 诗人基本信息 =====")
    print(result["poet_info"])

    print("\n\n===== 诗词及创作背景 =====")
    print(result["poems_with_context"])

    print("\n\n===== 诗词解析 =====")
    print(result["poem_analyses"])

    print("\n分析完成！")
    