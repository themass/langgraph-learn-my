#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单视频链接查找器
直接查找实际的视频流地址
"""

import requests
import re
import json
from urllib.parse import urlparse


def find_video_links(url):
    """查找视频链接"""
    print(f"🎬 查找视频链接: {url}")
    print("=" * 50)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://www.a3m5m.com/',
    })
    
    video_links = []
    
    try:
        # 获取页面内容
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        content = response.text
        print(f"✅ 获取页面成功，大小: {len(content)} 字符")
        
        # 查找实际的视频链接
        patterns = [
            # M3U8 流媒体
            r'https?://[^"\s<>]+\.m3u8[^"\s<>]*',
            # MP4 视频
            r'https?://[^"\s<>]+\.mp4[^"\s<>]*',
            # TS 视频片段
            r'https?://[^"\s<>]+\.ts[^"\s<>]*',
            # 其他视频格式
            r'https?://[^"\s<>]+\.(webm|avi|mov|flv|mkv)[^"\s<>]*',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if is_valid_video_url(match):
                    video_links.append(match)
        
        # 去重
        video_links = list(set(video_links))
        
        print(f"🎯 找到 {len(video_links)} 个视频链接:")
        for i, link in enumerate(video_links, 1):
            print(f"  {i}. {link}")
        
        if not video_links:
            print("❌ 未找到视频链接")
            print("💡 可能的原因:")
            print("  1. 视频链接是动态生成的")
            print("  2. 需要JavaScript执行才能获取")
            print("  3. 视频链接被加密或混淆")
            print("  4. 需要特定的请求头或认证")
        
    except Exception as e:
        print(f"❌ 获取失败: {e}")
    
    return video_links


def is_valid_video_url(url):
    """检查是否为有效的视频URL"""
    if not url or len(url) < 10:
        return False
    
    # 排除明显不是视频的URL
    exclude_patterns = [
        'javascript:', 'data:', 'mailto:', 'tel:', 'ftp:',
        '.css', '.js', '.json', '.xml', '.txt', '.pdf',
        'favicon', 'icon', 'logo', 'banner', 'advertisement'
    ]
    
    url_lower = url.lower()
    if any(pattern in url_lower for pattern in exclude_patterns):
        return False
    
    # 检查视频文件扩展名
    video_extensions = ['.mp4', '.webm', '.ogg', '.avi', '.mov', '.flv', '.mkv', '.m3u8', '.ts']
    if any(ext in url_lower for ext in video_extensions):
        return True
    
    return False


def try_common_video_patterns(base_url):
    """尝试常见的视频链接模式"""
    print(f"\n🔍 尝试常见视频链接模式...")
    
    video_id = base_url.split('/')[-1]
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    })
    
    # 常见的视频链接模式
    patterns = [
        f"https://mjs.szaction.cc/video/{video_id}.m3u8",
        f"https://mjs.szaction.cc/video/{video_id}.mp4",
        f"https://mjson.szaction.cc/video/{video_id}.m3u8",
        f"https://mjson.szaction.cc/video/{video_id}.mp4",
        f"https://cdn.a3m5m.com/video/{video_id}.m3u8",
        f"https://cdn.a3m5m.com/video/{video_id}.mp4",
        f"https://static.a3m5m.com/video/{video_id}.m3u8",
        f"https://static.a3m5m.com/video/{video_id}.mp4",
        f"https://assets.a3m5m.com/video/{video_id}.m3u8",
        f"https://assets.a3m5m.com/video/{video_id}.mp4",
        f"https://mjs.szaction.cc/stream/{video_id}.m3u8",
        f"https://mjs.szaction.cc/stream/{video_id}.mp4",
        f"https://mjson.szaction.cc/stream/{video_id}.m3u8",
        f"https://mjson.szaction.cc/stream/{video_id}.mp4",
        f"https://mjs.szaction.cc/media/{video_id}.m3u8",
        f"https://mjs.szaction.cc/media/{video_id}.mp4",
        f"https://mjson.szaction.cc/media/{video_id}.m3u8",
        f"https://mjson.szaction.cc/media/{video_id}.mp4",
    ]
    
    found_links = []
    
    for pattern in patterns:
        try:
            response = session.head(pattern, timeout=5)
            if response.status_code == 200:
                found_links.append(pattern)
                print(f"✅ 找到有效链接: {pattern}")
        except:
            continue
    
    if not found_links:
        print("❌ 未找到有效的视频链接")
    
    return found_links


def main():
    """主函数"""
    url = "https://www.a3m5m.com/s/video/shipin/1044455"
    
    # 方法1: 从页面内容中查找
    video_links = find_video_links(url)
    
    # 方法2: 尝试常见模式
    pattern_links = try_common_video_patterns(url)
    
    # 合并结果
    all_links = list(set(video_links + pattern_links))
    
    print(f"\n🎬 最终结果:")
    print("=" * 50)
    
    if all_links:
        print(f"✅ 找到 {len(all_links)} 个视频链接:")
        for i, link in enumerate(all_links, 1):
            print(f"  {i}. {link}")
    else:
        print("❌ 未找到任何视频链接")
        print("\n💡 建议:")
        print("  1. 使用浏览器开发者工具查看网络请求")
        print("  2. 检查页面是否有JavaScript动态加载")
        print("  3. 尝试使用Selenium等工具模拟浏览器")
        print("  4. 检查是否需要特定的认证或请求头")


if __name__ == "__main__":
    main()
