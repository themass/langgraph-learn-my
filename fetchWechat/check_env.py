#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速验证所有方案是否可用
"""

import sys

def check_core():
    """检查核心依赖"""
    print("检查核心依赖...")
    try:
        import requests
        import bs4
        from firecrawl import FirecrawlApp
        from loguru import logger
        print("  ✅ 核心依赖已安装")
        return True
    except ImportError as e:
        print(f"  ❌ 缺少核心依赖: {e}")
        print("     运行: pip install firecrawl-py loguru requests beautifulsoup4 lxml")
        return False

def check_selenium():
    """检查 Selenium"""
    print("\n检查 Selenium 方案...")
    try:
        from selenium import webdriver
        from webdriver_manager.chrome import ChromeDriverManager
        print("  ✅ Selenium 已安装")
        return True
    except ImportError:
        print("  ⚠️  Selenium 未安装（可选）")
        print("     运行: pip install selenium webdriver-manager")
        return False

def check_rsshub():
    """检查 RSSHub"""
    print("\n检查 RSSHub 方案...")
    try:
        import feedparser
        print("  ✅ feedparser 已安装")
        return True
    except ImportError:
        print("  ⚠️  feedparser 未安装（可选）")
        print("     运行: pip install feedparser")
        return False

def check_firecrawl_service():
    """检查 Firecrawl 服务"""
    print("\n检查 Firecrawl 服务...")
    try:
        import requests
        response = requests.get("http://localhost:3002/", timeout=2)
        if response.status_code == 200:
            print("  ✅ Firecrawl 服务运行正常")
            return True
        else:
            print(f"  ⚠️  Firecrawl 返回异常状态: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("  ❌ Firecrawl 服务未运行")
        print("     启动: cd /path/to/firecrawl && docker compose up -d")
        return False
    except Exception as e:
        print(f"  ❌ 检查失败: {e}")
        return False

def main():
    print("="*60)
    print("微信公众号文章采集器 - 环境检查")
    print("="*60)
    
    results = {
        'core': check_core(),
        'selenium': check_selenium(),
        'rsshub': check_rsshub(),
        'firecrawl': check_firecrawl_service()
    }
    
    print("\n" + "="*60)
    print("检查结果")
    print("="*60)
    
    if results['core'] and results['firecrawl']:
        print("\n✅ 核心功能可用")
    else:
        print("\n❌ 核心功能不可用，请先安装核心依赖和启动 Firecrawl")
    
    if results['selenium']:
        print("✅ Selenium 方案可用")
        print("   运行: python scraper_selenium.py '公众号名称' 10")
    else:
        print("⚠️  Selenium 方案不可用")
    
    if results['rsshub']:
        print("✅ RSSHub 方案可用")
        print("   运行: python scraper_rsshub.py 'biz参数' 10")
    else:
        print("⚠️  RSSHub 方案不可用")
    
    print("✅ 手动 URL 方案可用（无需额外依赖）")
    print("   运行: python scrape_direct_urls.py urls.txt '公众号名称'")
    
    print("\n" + "="*60)
    
    if results['core'] and results['firecrawl'] and (results['selenium'] or results['rsshub']):
        print("🎉 环境配置完成！可以开始使用")
        print("="*60)
        return 0
    else:
        print("⚠️  部分功能不可用，请按提示安装依赖")
        print("="*60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
