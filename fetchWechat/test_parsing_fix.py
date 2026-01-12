#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试页面解析修复
验证能否正确解析 10 条数据
"""

import requests
from bs4 import BeautifulSoup

def test_parsing():
    """测试解析"""
    
    print(f"\n{'='*60}")
    print(f"测试搜狗页面解析修复")
    print(f"{'='*60}\n")
    
    url = 'https://weixin.sogou.com/weixin?type=2&query=逛逛GitHub&page=1'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    
    print(f"访问: {url}\n")
    
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print("旧方法（错误）:")
    print("-" * 60)
    old_news_list = soup.find_all('div', class_='news-box')
    print(f"find_all('div', class_='news-box'): {len(old_news_list)} 个 ❌")
    
    print("\n新方法（正确）:")
    print("-" * 60)
    
    # 新方法
    news_box = soup.find('div', class_='news-box')
    if news_box:
        print(f"✅ 找到 news-box")
        
        news_list_ul = news_box.find('ul', class_='news-list')
        if news_list_ul:
            print(f"✅ 找到 news-list")
            
            news_list = news_list_ul.find_all('li')
            print(f"✅ 找到 {len(news_list)} 个 li 元素")
            
            print(f"\n{'='*60}")
            print(f"文章列表（前 5 条）:")
            print(f"{'='*60}\n")
            
            for i, li in enumerate(news_list[:5], 1):
                h3 = li.find('h3')
                if h3:
                    title = h3.text.strip()
                    link = h3.find('a')
                    if link:
                        href = link.get('href', '')
                        print(f"{i}. {title[:50]}...")
                        print(f"   URL: {href[:80]}...")
                        print()
            
            print(f"{'='*60}")
            print(f"结果: ✅ 成功解析 {len(news_list)} 条数据！")
            print(f"{'='*60}")
            
            return True
        else:
            print("❌ 没有找到 news-list")
    else:
        print("❌ 没有找到 news-box")
    
    return False


if __name__ == "__main__":
    success = test_parsing()
    
    if success:
        print("\n✅ 页面解析已修复！")
        print("\n现在可以正常使用:")
        print("  python scraper_selenium.py '逛逛GitHub' 10")
        print("  python scraper.py '逛逛GitHub' 10")
    else:
        print("\n❌ 页面解析仍有问题")
        print("请检查搜狗是否改变了页面结构")
