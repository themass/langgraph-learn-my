#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
生产级 RAG (Retrieval-Augmented Generation) 模块
=================================================

实现多种 RAG 模式：
1. 基础 RAG - 向量检索 + LLM 生成
2. Agentic RAG - 智能路由、多步检索、查询重写
3. LLM RAG - 使用 LLM 进行检索和生成

特点：
- 模拟向量数据库（可替换为真实向量数据库）
- 查询重写和扩展
- 多步检索策略
- 智能路由决策
- 生产级错误处理和日志
"""

from typing import List, Dict, Any, Optional, Tuple
from langchain_core.prompts import ChatPromptTemplate
from utils import get_llm
from log_utils import log_node_input, log_node_output, log_prompt
import json
import re
import random
from datetime import datetime


# =================================================================
# 模拟向量数据库
# =================================================================

class MockVectorDB:
    """模拟向量数据库"""
    
    def __init__(self):
        # 模拟文档库
        self.documents = [
            {
                "id": "doc-001",
                "content": "Python是一种高级编程语言，广泛用于数据科学、机器学习和Web开发。Python语法简洁，易于学习。",
                "metadata": {"category": "编程语言", "source": "技术文档"}
            },
            {
                "id": "doc-002",
                "content": "LangGraph是一个用于构建状态机图的库，特别适合构建AI代理。它提供了灵活的节点和边定义。",
                "metadata": {"category": "AI框架", "source": "技术文档"}
            },
            {
                "id": "doc-003",
                "content": "RAG（Retrieval-Augmented Generation）是一种结合检索和生成的技术，通过检索相关文档来增强LLM的生成能力。",
                "metadata": {"category": "AI技术", "source": "技术文档"}
            },
            {
                "id": "doc-004",
                "content": "向量数据库用于存储和检索高维向量，常用于相似度搜索。常见的向量数据库包括Pinecone、Weaviate、Qdrant等。",
                "metadata": {"category": "数据库", "source": "技术文档"}
            },
            {
                "id": "doc-005",
                "content": "查询重写是RAG中的重要技术，通过改写用户查询来提高检索准确性。常见方法包括查询扩展、查询分解等。",
                "metadata": {"category": "RAG技术", "source": "技术文档"}
            },
            {
                "id": "doc-006",
                "content": "Agentic RAG是一种智能RAG模式，使用LLM来决定检索策略，包括是否需要检索、检索什么、如何检索等。",
                "metadata": {"category": "RAG技术", "source": "技术文档"}
            },
            {
                "id": "doc-007",
                "content": "多步检索是Agentic RAG的核心特性，通过多轮检索逐步获取更精确的信息。",
                "metadata": {"category": "RAG技术", "source": "技术文档"}
            },
            {
                "id": "doc-008",
                "content": "LLM RAG使用大语言模型本身进行检索，通过生成查询、评估相关性等方式来获取信息。",
                "metadata": {"category": "RAG技术", "source": "技术文档"}
            }
        ]
    
    def similarity_search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """相似度搜索（模拟）"""
        # 简单的关键词匹配模拟相似度搜索
        query_lower = query.lower()
        scored_docs = []
        
        for doc in self.documents:
            content_lower = doc["content"].lower()
            # 计算简单的匹配分数
            score = 0
            query_words = query_lower.split()
            for word in query_words:
                if word in content_lower:
                    score += 1
            
            if score > 0:
                scored_docs.append({
                    **doc,
                    "score": score / len(query_words)  # 归一化分数
                })
        
        # 按分数排序
        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        
        return scored_docs[:top_k]
    
    def add_document(self, content: str, metadata: Optional[Dict] = None):
        """添加文档"""
        doc_id = f"doc-{len(self.documents) + 1:03d}"
        self.documents.append({
            "id": doc_id,
            "content": content,
            "metadata": metadata or {}
        })


# 全局向量数据库实例
vector_db = MockVectorDB()


# =================================================================
# RAG Prompt 模板
# =================================================================

RAG_SYSTEM_PROMPT = """你是一位专业的RAG系统专家，擅长进行查询重写、检索策略规划和答案生成。

你的任务：
1. 理解用户查询的意图
2. 重写查询以提高检索准确性
3. 规划检索策略
4. 基于检索结果生成高质量答案"""


QUERY_REWRITE_PROMPT = """请重写以下查询，以提高检索准确性：

原始查询：{query}

上下文信息：{context}

请考虑：
1. 扩展查询以包含相关关键词
2. 分解复杂查询为多个子查询
3. 添加领域特定的术语

返回JSON格式：
{{{{"rewritten_queries": ["重写查询1", "重写查询2", ...], "reasoning": "重写原因", "query_type": "查询类型（简单/复杂/多步骤）"}}}}"""


AGENTIC_ROUTING_PROMPT = """请分析以下查询，决定检索策略：

查询：{query}

历史检索结果：{previous_results}

请决定：
1. 是否需要进一步检索？
2. 如果需要，应该检索什么？
3. 检索策略是什么？

返回JSON格式：
{{{{"needs_retrieval": true/false, "retrieval_strategy": "检索策略描述", "query_variations": ["查询变体1", ...], "reasoning": "决策原因"}}}}"""


ANSWER_GENERATION_PROMPT = """基于以下检索结果，回答用户问题：

问题：{query}

检索到的文档：
{retrieved_docs}

请生成一个准确、完整的答案：
1. 基于检索结果回答问题
2. 如果检索结果不足，明确说明
3. 引用相关文档来源

返回JSON格式：
{{{{"answer": "答案内容", "sources": ["文档ID1", "文档ID2", ...], "confidence": "高/中/低", "missing_info": ["缺失信息1", ...]}}}}"""


def format_query_rewrite_prompt(query: str, context: str = "") -> str:
    """格式化查询重写 Prompt"""
    prompt = QUERY_REWRITE_PROMPT.format(query=query, context=context)
    return prompt


def format_agentic_routing_prompt(query: str, previous_results: str = "") -> str:
    """格式化 Agentic 路由 Prompt"""
    prompt = AGENTIC_ROUTING_PROMPT.format(query=query, previous_results=previous_results)
    return prompt


def format_answer_generation_prompt(query: str, retrieved_docs: str) -> str:
    """格式化答案生成 Prompt"""
    prompt = ANSWER_GENERATION_PROMPT.format(query=query, retrieved_docs=retrieved_docs)
    return prompt


# =================================================================
# 基础 RAG
# =================================================================

class BasicRAG:
    """基础 RAG - 向量检索 + LLM 生成"""
    
    def __init__(self, vector_db: MockVectorDB = None):
        self.vector_db = vector_db or MockVectorDB()
        self.llm = get_llm(temperature=0.3)
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """检索相关文档"""
        return self.vector_db.similarity_search(query, top_k=top_k)
    
    def generate(self, query: str, retrieved_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """基于检索结果生成答案"""
        # 准备检索文档文本
        docs_text = ""
        source_ids = []
        for i, doc in enumerate(retrieved_docs, 1):
            docs_text += f"\n文档{i} (ID: {doc['id']}):\n{doc['content']}\n"
            source_ids.append(doc['id'])
        
        # 格式化 Prompt
        human_prompt = format_answer_generation_prompt(query, docs_text)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", RAG_SYSTEM_PROMPT),
            ("human", human_prompt)
        ])
        
        log_prompt("basic_rag_generate", [
            ("system", RAG_SYSTEM_PROMPT),
            ("human", human_prompt)
        ])
        
        chain = prompt | self.llm
        result = chain.invoke({})
        
        # 解析结果
        try:
            json_str = re.search(r'\{.*\}', result.content, re.DOTALL)
            if json_str:
                answer_data = json.loads(json_str.group())
            else:
                answer_data = {
                    "answer": result.content,
                    "sources": source_ids,
                    "confidence": "中",
                    "missing_info": []
                }
        except:
            answer_data = {
                "answer": result.content,
                "sources": source_ids,
                "confidence": "中",
                "missing_info": []
            }
        
        return answer_data
    
    def query(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """完整的 RAG 查询流程"""
        log_node_input("basic_rag_query", {"query": query})
        
        # 检索
        retrieved_docs = self.retrieve(query, top_k)
        
        # 生成
        result = self.generate(query, retrieved_docs)
        
        output = {
            "query": query,
            "retrieved_docs": retrieved_docs,
            "answer": result.get("answer", ""),
            "sources": result.get("sources", []),
            "confidence": result.get("confidence", "中"),
            "missing_info": result.get("missing_info", [])
        }
        
        log_node_output("basic_rag_query", output)
        
        return output


# =================================================================
# Agentic RAG
# =================================================================

class AgenticRAG:
    """Agentic RAG - 智能路由、多步检索、查询重写"""
    
    def __init__(self, vector_db: MockVectorDB = None):
        self.vector_db = vector_db or MockVectorDB()
        self.llm = get_llm(temperature=0.3)
        self.max_iterations = 3  # 最多检索3轮
    
    def rewrite_query(self, query: str, context: str = "") -> Dict[str, Any]:
        """查询重写"""
        human_prompt = format_query_rewrite_prompt(query, context)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", RAG_SYSTEM_PROMPT),
            ("human", human_prompt)
        ])
        
        log_prompt("agentic_rag_rewrite", [
            ("system", RAG_SYSTEM_PROMPT),
            ("human", human_prompt)
        ])
        
        chain = prompt | self.llm
        result = chain.invoke({})
        
        try:
            json_str = re.search(r'\{.*\}', result.content, re.DOTALL)
            if json_str:
                rewrite_data = json.loads(json_str.group())
            else:
                rewrite_data = {
                    "rewritten_queries": [query],
                    "reasoning": "保持原查询",
                    "query_type": "简单"
                }
        except:
            rewrite_data = {
                "rewritten_queries": [query],
                "reasoning": "保持原查询",
                "query_type": "简单"
            }
        
        return rewrite_data
    
    def route(self, query: str, previous_results: List[Dict] = None) -> Dict[str, Any]:
        """智能路由 - 决定是否需要进一步检索"""
        previous_results_text = ""
        if previous_results:
            for i, res in enumerate(previous_results, 1):
                previous_results_text += f"\n检索轮次{i}: {len(res.get('docs', []))} 个文档"
        
        human_prompt = format_agentic_routing_prompt(query, previous_results_text)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", RAG_SYSTEM_PROMPT),
            ("human", human_prompt)
        ])
        
        log_prompt("agentic_rag_route", [
            ("system", RAG_SYSTEM_PROMPT),
            ("human", human_prompt)
        ])
        
        chain = prompt | self.llm
        result = chain.invoke({})
        
        try:
            json_str = re.search(r'\{.*\}', result.content, re.DOTALL)
            if json_str:
                route_data = json.loads(json_str.group())
            else:
                route_data = {
                    "needs_retrieval": True,
                    "retrieval_strategy": "直接检索",
                    "query_variations": [query],
                    "reasoning": "需要检索"
                }
        except:
            route_data = {
                "needs_retrieval": True,
                "retrieval_strategy": "直接检索",
                "query_variations": [query],
                "reasoning": "需要检索"
            }
        
        return route_data
    
    def multi_step_retrieve(self, query: str) -> Dict[str, Any]:
        """多步检索"""
        log_node_input("agentic_rag_multi_step", {"query": query})
        
        all_docs = []
        retrieval_history = []
        iteration = 0
        
        # 第一轮：查询重写
        rewrite_result = self.rewrite_query(query)
        rewritten_queries = rewrite_result.get("rewritten_queries", [query])
        
        while iteration < self.max_iterations:
            iteration += 1
            
            # 决定检索策略
            route_result = self.route(query, retrieval_history)
            
            if not route_result.get("needs_retrieval", True):
                break
            
            # 获取查询变体
            query_variations = route_result.get("query_variations", rewritten_queries)
            
            # 执行检索
            round_docs = []
            for q_var in query_variations[:2]:  # 最多使用2个查询变体
                docs = self.vector_db.similarity_search(q_var, top_k=3)
                round_docs.extend(docs)
            
            # 去重
            seen_ids = set()
            unique_docs = []
            for doc in round_docs:
                if doc['id'] not in seen_ids:
                    seen_ids.add(doc['id'])
                    unique_docs.append(doc)
            
            all_docs.extend(unique_docs)
            retrieval_history.append({
                "iteration": iteration,
                "query_variations": query_variations,
                "docs": unique_docs,
                "strategy": route_result.get("retrieval_strategy", "")
            })
            
            # 如果已经检索到足够信息，可以提前结束
            if len(all_docs) >= 5:  # 至少5个文档
                break
        
        # 去重并排序
        final_docs = []
        seen_ids = set()
        for doc in all_docs:
            if doc['id'] not in seen_ids:
                seen_ids.add(doc['id'])
                final_docs.append(doc)
        
        # 按分数排序
        final_docs.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        output = {
            "query": query,
            "rewritten_queries": rewritten_queries,
            "retrieved_docs": final_docs[:5],  # 返回top 5
            "retrieval_history": retrieval_history,
            "iterations": iteration
        }
        
        log_node_output("agentic_rag_multi_step", output)
        
        return output
    
    def query(self, query: str) -> Dict[str, Any]:
        """完整的 Agentic RAG 查询流程"""
        # 多步检索
        retrieval_result = self.multi_step_retrieve(query)
        
        # 生成答案
        basic_rag = BasicRAG(self.vector_db)
        answer_result = basic_rag.generate(query, retrieval_result["retrieved_docs"])
        
        return {
            **retrieval_result,
            **answer_result
        }


# =================================================================
# LLM RAG
# =================================================================

class LLMRAG:
    """LLM RAG - 使用 LLM 进行检索和生成"""
    
    def __init__(self, vector_db: MockVectorDB = None):
        self.vector_db = vector_db or MockVectorDB()
        self.llm = get_llm(temperature=0.3)
    
    def llm_retrieve(self, query: str) -> List[Dict[str, Any]]:
        """使用 LLM 生成检索查询"""
        # LLM 生成多个查询变体
        prompt_text = f"""请为以下查询生成3-5个检索查询变体，用于向量数据库检索：

原始查询：{query}

请考虑：
1. 同义词替换
2. 相关概念扩展
3. 不同角度的查询

返回JSON格式：
{{{{"queries": ["查询1", "查询2", ...], "reasoning": "生成原因"}}}}"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一位专业的检索查询生成专家。"),
            ("human", prompt_text)
        ])
        
        chain = prompt | self.llm
        result = chain.invoke({})
        
        try:
            json_str = re.search(r'\{.*\}', result.content, re.DOTALL)
            if json_str:
                query_data = json.loads(json_str.group())
                queries = query_data.get("queries", [query])
            else:
                queries = [query]
        except:
            queries = [query]
        
        # 使用生成的查询进行检索
        all_docs = []
        seen_ids = set()
        
        for q in queries:
            docs = self.vector_db.similarity_search(q, top_k=2)
            for doc in docs:
                if doc['id'] not in seen_ids:
                    seen_ids.add(doc['id'])
                    all_docs.append(doc)
        
        # 使用 LLM 评估文档相关性
        docs_text = ""
        for i, doc in enumerate(all_docs, 1):
            docs_text += f"\n文档{i} (ID: {doc['id']}):\n{doc['content']}\n"
        
        evaluation_prompt = f"""请评估以下文档与查询的相关性：

查询：{query}

文档：
{docs_text}

返回JSON格式：
{{{{"relevant_docs": ["文档ID1", "文档ID2", ...], "reasoning": "相关性评估"}}}}"""
        
        eval_prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一位专业的文档相关性评估专家。"),
            ("human", evaluation_prompt)
        ])
        
        eval_chain = eval_prompt | self.llm
        eval_result = eval_chain.invoke({})
        
        try:
            json_str = re.search(r'\{.*\}', eval_result.content, re.DOTALL)
            if json_str:
                eval_data = json.loads(json_str.group())
                relevant_ids = set(eval_data.get("relevant_docs", []))
                filtered_docs = [doc for doc in all_docs if doc['id'] in relevant_ids]
            else:
                filtered_docs = all_docs[:3]  # 默认返回前3个
        except:
            filtered_docs = all_docs[:3]
        
        return filtered_docs
    
    def query(self, query: str) -> Dict[str, Any]:
        """完整的 LLM RAG 查询流程"""
        log_node_input("llm_rag_query", {"query": query})
        
        # LLM 检索
        retrieved_docs = self.llm_retrieve(query)
        
        # 生成答案
        basic_rag = BasicRAG(self.vector_db)
        answer_result = basic_rag.generate(query, retrieved_docs)
        
        output = {
            "query": query,
            "retrieved_docs": retrieved_docs,
            **answer_result
        }
        
        log_node_output("llm_rag_query", output)
        
        return output


# =================================================================
# 工具函数
# =================================================================

def rag_tool(query: str, mode: str = "basic") -> Dict[str, Any]:
    """
    RAG 工具函数 - 可用于 ReAct 等模式
    
    Args:
        query: 查询文本
        mode: RAG 模式 ("basic", "agentic", "llm")
    
    Returns:
        RAG 查询结果
    """
    if mode == "basic":
        rag = BasicRAG()
    elif mode == "agentic":
        rag = AgenticRAG()
    elif mode == "llm":
        rag = LLMRAG()
    else:
        rag = BasicRAG()
    
    return rag.query(query)


# =================================================================
# Demo
# =================================================================

def demo_rag():
    """RAG 模块 Demo"""
    
    print("=" * 60)
    print("生产级 RAG 模块 Demo")
    print("=" * 60)
    
    test_queries = [
        "什么是RAG？",
        "Agentic RAG和普通RAG有什么区别？",
        "如何使用向量数据库进行检索？"
    ]
    
    # 测试三种 RAG 模式
    for mode_name, rag_class in [
        ("基础 RAG", BasicRAG),
        ("Agentic RAG", AgenticRAG),
        ("LLM RAG", LLMRAG)
    ]:
        print(f"\n{'='*60}")
        print(f"【{mode_name}】")
        print(f"{'='*60}")
        
        rag = rag_class()
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n查询 {i}: {query}")
            print("-" * 60)
            
            result = rag.query(query)
            
            print(f"检索到 {len(result.get('retrieved_docs', []))} 个文档")
            print(f"答案: {result.get('answer', '未生成')[:200]}...")
            print(f"置信度: {result.get('confidence', '未知')}")
            print(f"来源: {', '.join(result.get('sources', []))}")
            
            if 'retrieval_history' in result:
                print(f"检索轮次: {result.get('iterations', 0)}")
            
            print()


if __name__ == "__main__":
    demo_rag()
