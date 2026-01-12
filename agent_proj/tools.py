#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
工具库：定义 Agent 所需的外部工具
包含：
1. Tavily Search (市场搜素)
2. URL Scraper (深度阅读)
3. Financial Data (财报数据 - 使用 yfinance)
"""

import os
import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool
from typing import Dict, Union, List
from dotenv import load_dotenv
from pathlib import Path

# 加载项目根目录的 .env 文件
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# 尝试导入可选依赖
try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None

try:
    import yfinance as yf
except ImportError:
    yf = None

# ==============================================================================
# 1. 市场搜索工具 (Search Tool)
# ==============================================================================

@tool
def search_market_data(query: str) -> str:
    """
    Search for real-time market data, news, and industry trends using Tavily API.
    Use this tool to find qualitative information, recent news, or general industry reports.
    
    Args:
        query: The search query string (e.g., "Nvidia 2024 revenue forecast").
    """
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return (
            "Error: TAVILY_API_KEY not found!\n"
            "请在项目根目录的 .env 文件中配置:\n"
            "  TAVILY_API_KEY=your_api_key_here\n"
            "\n"
            "获取 API Key: https://tavily.com/"
        )

    if not TavilyClient:
        return "Error: 'tavily-python' library not installed. Please install it via pip."

    try:
        client = TavilyClient(api_key=api_key)
        # 使用 search_depth="advanced" 获取更详细的上下文
        response = client.search(query=query, search_depth="advanced", max_results=5)
        
        # 格式化输出
        results = []
        for res in response.get("results", []):
            title = res.get("title", "No Title")
            url = res.get("url", "#")
            content = res.get("content", "")[:500] # 限制每个结果的长度
            results.append(f"Source: [{title}]({url})\nSummary: {content}\n")
            
        return "\n---\n".join(results)
    except Exception as e:
        return f"Error executing search: {str(e)}"

# ==============================================================================
# 2. 网页抓取工具 (Scraper Tool)
# ==============================================================================

@tool
def scrape_web_content(url: str) -> str:
    """
    Scrape and extract text content from a specific URL.
    Use this tool when you need to read the full details of a search result or a report.
    
    Args:
        url: The full URL to scrape.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 移除脚本和样式
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
            
        text = soup.get_text()
        
        # 清洗空白字符
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # 截断过长内容，保留前 4000 字符 (约为 1-2k tokens)
        return clean_text[:4000] + ("\n...[Content Truncated]" if len(clean_text) > 4000 else "")
        
    except Exception as e:
        return f"Error scraping URL {url}: {str(e)}"

# ==============================================================================
# 3. 财经数据工具 (Financial Tool)
# ==============================================================================

@tool
def get_financial_metrics(ticker: str) -> Union[Dict, str]:
    """
    Get key financial metrics for a specific public company using its stock ticker.
    Metrics include: Market Cap, PE Ratio, Revenue, Profit Margins, etc.
    
    Args:
        ticker: The stock ticker symbol (e.g., "AAPL", "NVDA", "MSFT").
    """
    if not yf:
        return "Error: 'yfinance' library not installed. Please install it via pip."
        
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # 提取关键指标，避免返回过多无关数据
        metrics = {
            "Company": info.get("longName"),
            "Sector": info.get("sector"),
            "CurrentPrice": info.get("currentPrice"),
            "MarketCap": info.get("marketCap"),
            "TrailingPE": info.get("trailingPE"),
            "ForwardPE": info.get("forwardPE"),
            "RevenueGrowth": info.get("revenueGrowth"),
            "ProfitMargins": info.get("profitMargins"),
            "52WeekHigh": info.get("fiftyTwoWeekHigh"),
            "52WeekLow": info.get("fiftyTwoWeekLow"),
            "Description": info.get("longBusinessSummary", "")[:300] + "..."
        }
        
        # 过滤掉 None 值
        clean_metrics = {k: v for k, v in metrics.items() if v is not None}
        return clean_metrics
        
    except Exception as e:
        return f"Error getting financial data for {ticker}: {str(e)}"
