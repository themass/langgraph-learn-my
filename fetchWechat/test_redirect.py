#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试搜狗重定向跟踪
"""

import requests
from bs4 import BeautifulSoup
import sys

def test_redirect(sogou_url: str):
    """测试跟踪搜狗重定向"""
    print(f"\n{'='*60}")
    print(f"测试 URL: {sogou_url[:100]}...")
    print(f"{'='*60}\n")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://weixin.sogou.com/'
    }
    
    # 方法1: allow_redirects=True
    print("方法1: requests.get(allow_redirects=True)")
    try:
        session = requests.Session()
        session.headers.update(headers)
        response = session.get(sogou_url, timeout=10, allow_redirects=True)
        print(f"  最终 URL: {response.url}")
        print(f"  状态码: {response.status_code}")
        print(f"  内容长度: {len(response.text)} 字符")
        
        if 'mp.weixin.qq.com' in response.url:
            print(f"  ✅ 成功跟踪到微信文章!")
            return response.url
        else:
            print(f"  ⚠️ 未跟踪到微信文章")
            # 尝试从HTML中找线索
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找 meta refresh
            meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
            if meta_refresh:
                print(f"  发现 meta refresh: {meta_refresh.get('content', '')[:100]}")
            
            # 查找可能的跳转链接
            links = soup.find_all('a', href=True)
            wx_links = [link['href'] for link in links if 'mp.weixin.qq.com' in link['href']]
            if wx_links:
                print(f"  发现微信链接: {wx_links[0]}")
                return wx_links[0]
            
            # 打印页面标题
            title = soup.find('title')
            if title:
                print(f"  页面标题: {title.text}")
            
            # 打印部分内容
            print(f"\n  页面内容预览:")
            print(f"  {response.text[:500]}")
            
    except Exception as e:
        print(f"  ❌ 失败: {e}")
    
    print()
    
    # 方法2: allow_redirects=False
    print("方法2: requests.get(allow_redirects=False)")
    try:
        response = requests.get(sogou_url, headers=headers, timeout=10, allow_redirects=False)
        print(f"  状态码: {response.status_code}")
        
        if 300 <= response.status_code < 400:
            location = response.headers.get('Location', '')
            print(f"  Location 头: {location[:100] if location else '(无)'}")
            if 'mp.weixin.qq.com' in location:
                print(f"  ✅ 找到微信文章 URL!")
                return location
        
    except Exception as e:
        print(f"  ❌ 失败: {e}")
    
    print(f"\n{'='*60}")
    print(f"结论: 无法跟踪到真实的微信文章 URL")
    print(f"原因: 搜狗反爬虫机制")
    print(f"{'='*60}\n")
    
    return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python test_redirect.py <搜狗重定向URL>")
        print("\n示例:")
        print('  python test_redirect.py "https://weixin.sogou.com/link?url=xxx"')
        sys.exit(1)
    
    test_url = sys.argv[1]
    result = test_redirect(test_url)
    
    if result:
        print(f"✅ 真实 URL: {result}")
    else:
        print(f"❌ 无法获取真实 URL")
