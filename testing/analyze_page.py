#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
页面信息分析工具
详细分析获取到的网页内容
"""

import json
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re


def analyze_page_data(json_file):
    """分析页面数据"""
    print("🔍 页面信息详细分析")
    print("=" * 60)
    
    # 读取JSON数据
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 基本信息
    print("📋 基本信息:")
    print(f"  目标URL: {data['url']}")
    print(f"  实际URL: {data['current_url']}")
    print(f"  页面标题: {data['title']}")
    print(f"  内容长度: {data['content_length']} 字符")
    print(f"  获取方法: {data['method']}")
    print()
    
    # 页面状态分析
    print("🛡️ 页面状态分析:")
    text_content = data['text_content'].lower()
    
    if 'cloudflare' in text_content:
        print("  ✅ 检测到Cloudflare保护")
    if 'challenge' in text_content:
        print("  ✅ 检测到验证挑战")
    if 'verification' in text_content or '验证' in text_content:
        print("  ✅ 检测到验证机制")
    if 'captcha' in text_content:
        print("  ✅ 检测到验证码")
    if 'turnstile' in text_content:
        print("  ✅ 检测到Turnstile验证")
    
    # 提取Ray ID
    ray_id_match = re.search(r'Ray ID: ([a-f0-9]+)', data['text_content'])
    if ray_id_match:
        print(f"  🔍 Cloudflare Ray ID: {ray_id_match.group(1)}")
    
    print()
    
    # 内容分析
    print("📖 内容分析:")
    print(f"  文本长度: {len(data['text_content'])} 字符")
    print(f"  链接数量: {len(data['links'])}")
    print(f"  图片数量: {len(data['images'])}")
    print(f"  视频数量: {len(data['videos'])}")
    print()
    
    # 详细文本内容
    print("📝 完整文本内容:")
    print("-" * 40)
    print(data['text_content'])
    print()
    
    # 链接分析
    if data['links']:
        print("🔗 链接详细分析:")
        print("-" * 40)
        for i, link in enumerate(data['links'], 1):
            print(f"{i}. 文本: {link['text']}")
            print(f"   URL: {link['url']}")
            print(f"   域名: {urlparse(link['url']).netloc}")
            print()
    
    # 图片分析
    if data['images']:
        print("🖼️ 图片详细分析:")
        print("-" * 40)
        for i, img in enumerate(data['images'], 1):
            print(f"{i}. 描述: {img['alt']}")
            print(f"   URL: {img['url']}")
            print(f"   域名: {urlparse(img['url']).netloc}")
            print()
    
    # 视频分析
    if data['videos']:
        print("🎬 视频详细分析:")
        print("-" * 40)
        for i, video in enumerate(data['videos'], 1):
            print(f"{i}. 视频URL: {video['url']}")
            if video.get('poster'):
                print(f"   封面: {video['poster']}")
            print()
    else:
        print("🎬 视频分析: 未检测到视频元素")
        print()
    
    # HTML结构分析
    print("🏗️ HTML结构分析:")
    print("-" * 40)
    try:
        soup = BeautifulSoup(data['raw_html'], 'html.parser')
        
        # 统计各种标签
        tags = {}
        for tag in soup.find_all():
            tag_name = tag.name
            tags[tag_name] = tags.get(tag_name, 0) + 1
        
        print("标签统计:")
        for tag, count in sorted(tags.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {tag}: {count}个")
        
        # 查找表单
        forms = soup.find_all('form')
        if forms:
            print(f"\n表单数量: {len(forms)}")
            for i, form in enumerate(forms, 1):
                action = form.get('action', '无')
                method = form.get('method', 'GET')
                print(f"  表单{i}: action={action}, method={method}")
        
        # 查找脚本
        scripts = soup.find_all('script')
        if scripts:
            print(f"\n脚本数量: {len(scripts)}")
            for i, script in enumerate(scripts, 1):
                src = script.get('src', '内联脚本')
                print(f"  脚本{i}: {src}")
        
        # 查找样式表
        styles = soup.find_all('link', rel='stylesheet')
        if styles:
            print(f"\n样式表数量: {len(styles)}")
            for i, style in enumerate(styles, 1):
                href = style.get('href', '无')
                print(f"  样式表{i}: {href}")
        
    except Exception as e:
        print(f"HTML分析出错: {e}")
    
    print()
    
    # 安全分析
    print("🔒 安全分析:")
    print("-" * 40)
    
    # 检查HTTPS
    if data['url'].startswith('https://'):
        print("  ✅ 使用HTTPS加密")
    else:
        print("  ⚠️ 未使用HTTPS加密")
    
    # 检查外部资源
    external_domains = set()
    for link in data['links']:
        domain = urlparse(link['url']).netloc
        if domain and domain != urlparse(data['url']).netloc:
            external_domains.add(domain)
    
    for img in data['images']:
        domain = urlparse(img['url']).netloc
        if domain and domain != urlparse(data['url']).netloc:
            external_domains.add(domain)
    
    if external_domains:
        print(f"  🔍 外部域名: {', '.join(external_domains)}")
    else:
        print("  ✅ 无外部域名引用")
    
    print()
    
    # 文件信息
    print("📁 文件信息:")
    print("-" * 40)
    if data.get('screenshot'):
        screenshot_path = data['screenshot']
        if os.path.exists(screenshot_path):
            size = os.path.getsize(screenshot_path)
            print(f"  截图文件: {screenshot_path}")
            print(f"  截图大小: {size} 字节")
        else:
            print(f"  截图文件: {screenshot_path} (文件不存在)")
    
    json_size = os.path.getsize(json_file)
    print(f"  数据文件: {json_file}")
    print(f"  数据大小: {json_size} 字节")
    print()


def main():
    """主函数"""
    # 找到最新的数据文件
    files = [f for f in os.listdir('.') if f.startswith('enhanced_scraped_') and f.endswith('.json')]
    
    if not files:
        print("❌ 未找到数据文件")
        print("请先运行 enhanced_selenium_scraper.py 获取数据")
        return
    
    # 使用最新的文件
    latest_file = max(files, key=os.path.getctime)
    print(f"📄 分析文件: {latest_file}")
    print()
    
    analyze_page_data(latest_file)


if __name__ == "__main__":
    main()
