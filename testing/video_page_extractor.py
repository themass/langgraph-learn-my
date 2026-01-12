#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频页面提取器
从视频列表页面提取视频链接并分析视频页面内容
"""

import requests
import json
import time
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


def extract_video_links_from_list(content, base_url):
    """
    从列表页面提取视频链接
    
    Args:
        content: 页面内容
        base_url: 基础URL
    
    Returns:
        视频链接列表
    """
    soup = BeautifulSoup(content, 'html.parser')
    video_links = []
    
    # 查找所有链接
    links = soup.find_all('a', href=True)
    
    for link in links:
        href = link.get('href')
        if href:
            # 转换为绝对URL
            if href.startswith('/'):
                full_url = urljoin(base_url, href)
            elif href.startswith('http'):
                full_url = href
            else:
                full_url = urljoin(base_url, href)
            
            # 检查是否是视频链接
            if '/video/' in full_url or 'video' in full_url.lower():
                video_links.append(full_url)
    
    # 去重
    video_links = list(set(video_links))
    
    return video_links


def analyze_video_page(url):
    """
    分析单个视频页面
    
    Args:
        url: 视频页面URL
    
    Returns:
        视频页面分析结果
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://jptt.tv/',
    }
    
    try:
        print(f"🔍 分析视频页面: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        analysis = {
            'url': url,
            'title': None,
            'description': None,
            'video_links': [],
            'image_links': [],
            'has_encrypted_js': False,
            'has_dplayer': False,
            'has_hls': False,
            'status_code': response.status_code
        }
        
        # 获取标题
        title_tag = soup.find('title')
        if title_tag:
            analysis['title'] = title_tag.get_text().strip()
        
        # 获取描述
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            analysis['description'] = meta_desc.get('content', '').strip()
        
        # 查找视频链接
        content = response.text
        
        # 查找M3U8链接
        m3u8_pattern = r'https?://[^"\s<>]+\.m3u8[^"\s<>]*'
        m3u8_matches = re.findall(m3u8_pattern, content, re.IGNORECASE)
        analysis['video_links'].extend(m3u8_matches)
        
        # 查找MP4链接
        mp4_pattern = r'https?://[^"\s<>]+\.mp4[^"\s<>]*'
        mp4_matches = re.findall(mp4_pattern, content, re.IGNORECASE)
        analysis['video_links'].extend(mp4_matches)
        
        # 查找其他视频格式
        other_video_pattern = r'https?://[^"\s<>]+\.(webm|avi|mov|flv|mkv|ts)[^"\s<>]*'
        other_matches = re.findall(other_video_pattern, content, re.IGNORECASE)
        analysis['video_links'].extend(other_matches)
        
        # 去重
        analysis['video_links'] = list(set(analysis['video_links']))
        
        # 查找图片链接
        img_tags = soup.find_all('img', src=True)
        for img in img_tags:
            src = img.get('src')
            if src:
                if src.startswith('/'):
                    src = urljoin(url, src)
                analysis['image_links'].append(src)
        
        # 检查是否有加密的JavaScript
        if 'eval(' in content and 'I(' in content:
            analysis['has_encrypted_js'] = True
        
        # 检查是否有DPlayer
        if 'DPlayer' in content or 'dplayer' in content.lower():
            analysis['has_dplayer'] = True
        
        # 检查是否有HLS
        if 'hls' in content.lower() or '.m3u8' in content:
            analysis['has_hls'] = True
        
        return analysis
        
    except Exception as e:
        return {
            'url': url,
            'error': str(e),
            'status_code': getattr(e, 'response', {}).get('status_code', None) if hasattr(e, 'response') else None
        }


def main():
    """主函数"""
    print("🎬 视频页面提取器")
    print("=" * 60)
    
    # 读取之前保存的页面内容
    try:
        with open("final_page_content.html", "r", encoding="utf-8") as f:
            list_page_content = f.read()
        
        print("📄 读取列表页面内容...")
        
        # 提取视频链接
        base_url = "https://jptt.tv"
        video_links = extract_video_links_from_list(list_page_content, base_url)
        
        print(f"✅ 找到 {len(video_links)} 个视频链接")
        
        # 显示前10个视频链接
        print(f"\n🎬 前10个视频链接:")
        for i, link in enumerate(video_links[:10], 1):
            print(f"{i:2d}. {link}")
        
        if len(video_links) > 10:
            print(f"... 还有 {len(video_links) - 10} 个视频链接")
        
        # 分析前5个视频页面
        print(f"\n🔍 分析前5个视频页面...")
        video_analyses = []
        
        for i, video_url in enumerate(video_links[:5], 1):
            print(f"\n--- 分析第 {i} 个视频 ---")
            analysis = analyze_video_page(video_url)
            video_analyses.append(analysis)
            
            if 'error' in analysis:
                print(f"❌ 分析失败: {analysis['error']}")
            else:
                print(f"✅ 分析成功")
                print(f"  标题: {analysis['title']}")
                print(f"  视频链接数: {len(analysis['video_links'])}")
                print(f"  加密JS: {'是' if analysis['has_encrypted_js'] else '否'}")
                print(f"  DPlayer: {'是' if analysis['has_dplayer'] else '否'}")
                print(f"  HLS: {'是' if analysis['has_hls'] else '否'}")
                
                if analysis['video_links']:
                    print(f"  视频链接:")
                    for j, vlink in enumerate(analysis['video_links'][:3], 1):
                        print(f"    {j}. {vlink}")
                    if len(analysis['video_links']) > 3:
                        print(f"    ... 还有 {len(analysis['video_links']) - 3} 个")
            
            # 避免请求过快
            time.sleep(1)
        
        # 保存分析结果
        result = {
            'list_url': 'https://jptt.tv/list?idx=2&sort=2',
            'total_video_links': len(video_links),
            'video_links': video_links,
            'video_analyses': video_analyses
        }
        
        with open("video_pages_analysis.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 分析结果已保存到: video_pages_analysis.json")
        
        # 统计信息
        print(f"\n📊 统计信息:")
        print(f"  总视频链接数: {len(video_links)}")
        print(f"  成功分析的页面: {len([a for a in video_analyses if 'error' not in a])}")
        print(f"  包含加密JS的页面: {len([a for a in video_analyses if a.get('has_encrypted_js', False)])}")
        print(f"  包含DPlayer的页面: {len([a for a in video_analyses if a.get('has_dplayer', False)])}")
        print(f"  包含HLS的页面: {len([a for a in video_analyses if a.get('has_hls', False)])}")
        
        # 查找有视频链接的页面
        pages_with_videos = [a for a in video_analyses if a.get('video_links')]
        if pages_with_videos:
            print(f"\n🎬 找到视频链接的页面:")
            for page in pages_with_videos:
                print(f"  - {page['title']}")
                print(f"    URL: {page['url']}")
                print(f"    视频链接: {len(page['video_links'])} 个")
                for vlink in page['video_links'][:2]:
                    print(f"      {vlink}")
                if len(page['video_links']) > 2:
                    print(f"      ... 还有 {len(page['video_links']) - 2} 个")
                print()
        
    except FileNotFoundError:
        print("❌ 未找到 final_page_content.html 文件")
        print("请先运行 redirect_analyzer.py")
    except Exception as e:
        print(f"❌ 处理失败: {e}")
    
    print(f"\n🎉 视频页面提取完成!")


if __name__ == "__main__":
    main()
