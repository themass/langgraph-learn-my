#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试 Firecrawl 是否能直接处理搜狗重定向链接
"""

from firecrawl import FirecrawlApp
import sys

def test_firecrawl_redirect(sogou_url: str):
    """测试 Firecrawl 处理搜狗重定向"""
    
    print(f"\n{'='*60}")
    print(f"测试 Firecrawl 处理搜狗重定向")
    print(f"{'='*60}\n")
    print(f"搜狗链接: {sogou_url[:100]}...\n")
    
    firecrawl = FirecrawlApp(api_url="http://localhost:3002")
    
    print("方法1: 基础配置")
    print("-" * 60)
    try:
        result = firecrawl.scrape(
            url=sogou_url,
            formats=['markdown', 'html']
        )
        
        markdown = result.markdown if hasattr(result, 'markdown') else ''
        metadata = result.metadata if hasattr(result, 'metadata') else {}
        
        # 安全获取 metadata
        if hasattr(metadata, '__dict__'):
            title = getattr(metadata, 'title', 'N/A')
        else:
            title = metadata.get('title', 'N/A') if isinstance(metadata, dict) else 'N/A'
        
        print(f"✅ 抓取成功!")
        print(f"   内容长度: {len(markdown)} 字符")
        print(f"   标题: {title}")
        print(f"   内容预览:\n{markdown[:300]}\n")
        
        if len(markdown) > 500 and 'mp.weixin.qq.com' not in markdown:
            print(f"\n🎉 成功！Firecrawl 自动处理了重定向！")
            return True
        else:
            print(f"\n⚠️ 内容可能不是真实文章")
            
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    print("\n" + "-" * 60)
    print("方法2: 增加等待时间（处理 JavaScript 重定向）")
    print("-" * 60)
    try:
        result = firecrawl.scrape(
            url=sogou_url,
            formats=['markdown', 'html'],
            wait_for=10000,  # 等待 10 秒
            timeout=30000    # 总超时 30 秒
        )
        
        markdown = result.markdown if hasattr(result, 'markdown') else ''
        metadata = result.metadata if hasattr(result, 'metadata') else {}
        
        # 安全获取 metadata
        if hasattr(metadata, '__dict__'):
            title = getattr(metadata, 'title', 'N/A')
        else:
            title = metadata.get('title', 'N/A') if isinstance(metadata, dict) else 'N/A'
        
        print(f"✅ 抓取成功!")
        print(f"   内容长度: {len(markdown)} 字符")
        print(f"   标题: {title}")
        print(f"   内容预览:\n{markdown[:300]}\n")
        
        if len(markdown) > 500:
            print(f"\n🎉 成功！Firecrawl 处理了重定向！")
            return True
        else:
            print(f"\n⚠️ 内容可能不完整")
            
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    print("\n" + "-" * 60)
    print("方法3: 完整配置（模拟真实浏览器）")
    print("-" * 60)
    try:
        result = firecrawl.scrape(
            url=sogou_url,
            formats=['markdown', 'html'],
            only_main_content=True,
            wait_for=10000,
            timeout=30000,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            }
        )
        
        markdown = result.markdown if hasattr(result, 'markdown') else ''
        metadata = result.metadata if hasattr(result, 'metadata') else {}
        
        # 安全获取 metadata
        if hasattr(metadata, '__dict__'):
            title = getattr(metadata, 'title', 'N/A')
        else:
            title = metadata.get('title', 'N/A') if isinstance(metadata, dict) else 'N/A'
        
        print(f"✅ 抓取成功!")
        print(f"   内容长度: {len(markdown)} 字符")
        print(f"   标题: {title}")
        print(f"   内容预览:\n{markdown[:300]}\n")
        
        if len(markdown) > 500:
            print(f"\n🎉 成功！Firecrawl 处理了重定向！")
            return True
        else:
            print(f"\n⚠️ 内容可能不完整")
            
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    print("\n" + "="*60)
    print("结论:")
    print("="*60)
    print("如果以上方法都失败，说明 Firecrawl 无法处理搜狗反爬虫")
    print("原因: 搜狗会检测并阻止自动化工具（即使是真实浏览器）")
    print("建议: 使用 Selenium 方案或 RSSHub 方案")
    print("="*60)
    
    return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python test_firecrawl_redirect.py <搜狗重定向URL>")
        print("\n使用之前测试过的链接:")
        test_url = "https://weixin.sogou.com/link?url=dn9a_-gY295K0Rci_xozVXfdMkSQTLW6cwJThYulHEtVjXrGTiVgS_3bmdfpxqsDH9H1IG2zKfX70hdq0v-hXVqXa8Fplpd9EUZ7CrkL2FlL0dYcBm0ZEbfI3OvOxTAsS-ACiBSeYMD-OFJTnpZyDbbZ_9mLeD_yo3lnfBuEGZNWbAlFEVylcD_Ay3P4lRlN6epPpRgSZ8Roc0n-9vzSkMMPD7l7tVmJvse4O4I5uvY6D089ZA9Tb4b_inpApX0GtocSwS1izLi54z_tGSZTqA..&type=2&query=%E9%80%9B%E9%80%9BGitHub&token=8C4883E4A34BB67D7D7A3475D86B1DB47D2A086769626529"
    else:
        test_url = sys.argv[1]
    
    test_firecrawl_redirect(test_url)
