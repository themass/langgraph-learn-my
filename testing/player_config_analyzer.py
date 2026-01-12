#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
播放器配置分析器
分析JWPlayer和FluidPlayer的配置，查找视频源
"""

import requests
import json
import re
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


def analyze_jwplayer_config(content, base_url):
    """
    分析JWPlayer配置
    
    Args:
        content: 页面内容
        base_url: 基础URL
    
    Returns:
        JWPlayer配置信息
    """
    jwplayer_info = {
        'has_jwplayer': False,
        'configs': [],
        'video_sources': [],
        'playlist_urls': []
    }
    
    # 查找JWPlayer配置
    jwplayer_patterns = [
        r'jwplayer\s*\(\s*["\'][^"\']*["\']\s*\)\s*\.setup\s*\(\s*(\{[^}]+\})',
        r'jwplayer\s*\(\s*["\'][^"\']*["\']\s*\)\s*\.load\s*\(\s*(\{[^}]+\})',
        r'jwplayer\s*\(\s*["\'][^"\']*["\']\s*\)\s*\.setup\s*\(\s*(\{[^}]+(?:{[^}]*}[^}]*)*\})',
    ]
    
    for pattern in jwplayer_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            jwplayer_info['has_jwplayer'] = True
            jwplayer_info['configs'].append(match)
            
            # 在配置中查找视频源
            video_patterns = [
                r'["\']file["\']\s*:\s*["\']([^"\']+)["\']',
                r'["\']sources["\']\s*:\s*\[([^\]]+)\]',
                r'["\']playlist["\']\s*:\s*\[([^\]]+)\]',
                r'https?://[^"\s<>]+\.(m3u8|mp4|webm|avi|mov|flv|mkv|ts)[^"\s<>]*'
            ]
            
            for vpattern in video_patterns:
                vmatches = re.findall(vpattern, match, re.IGNORECASE)
                jwplayer_info['video_sources'].extend(vmatches)
    
    # 去重
    jwplayer_info['video_sources'] = list(set(jwplayer_info['video_sources']))
    
    return jwplayer_info


def analyze_fluidplayer_config(content, base_url):
    """
    分析FluidPlayer配置
    
    Args:
        content: 页面内容
        base_url: 基础URL
    
    Returns:
        FluidPlayer配置信息
    """
    fluidplayer_info = {
        'has_fluidplayer': False,
        'configs': [],
        'video_sources': []
    }
    
    # 查找FluidPlayer配置
    fluidplayer_patterns = [
        r'fluidPlayer\s*\(\s*["\'][^"\']*["\']\s*,\s*(\{[^}]+\})',
        r'new\s+FluidPlayer\s*\(\s*["\'][^"\']*["\']\s*,\s*(\{[^}]+\})',
    ]
    
    for pattern in fluidplayer_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            fluidplayer_info['has_fluidplayer'] = True
            fluidplayer_info['configs'].append(match)
            
            # 在配置中查找视频源
            video_patterns = [
                r'["\']src["\']\s*:\s*["\']([^"\']+)["\']',
                r'["\']sources["\']\s*:\s*\[([^\]]+)\]',
                r'https?://[^"\s<>]+\.(m3u8|mp4|webm|avi|mov|flv|mkv|ts)[^"\s<>]*'
            ]
            
            for vpattern in video_patterns:
                vmatches = re.findall(vpattern, match, re.IGNORECASE)
                fluidplayer_info['video_sources'].extend(vmatches)
    
    # 去重
    fluidplayer_info['video_sources'] = list(set(fluidplayer_info['video_sources']))
    
    return fluidplayer_info


def analyze_ajax_requests(content, base_url):
    """
    分析AJAX请求，查找可能的视频API
    
    Args:
        content: 页面内容
        base_url: 基础URL
    
    Returns:
        AJAX请求信息
    """
    ajax_info = {
        'ajax_requests': [],
        'api_endpoints': [],
        'video_apis': []
    }
    
    # 查找AJAX请求
    ajax_patterns = [
        r'\.ajax\s*\(\s*\{[^}]+\}',
        r'fetch\s*\(\s*["\']([^"\']+)["\']',
        r'XMLHttpRequest\s*\(\s*["\']([^"\']+)["\']',
        r'axios\s*\.\s*(get|post)\s*\(\s*["\']([^"\']+)["\']',
    ]
    
    for pattern in ajax_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
        ajax_info['ajax_requests'].extend(matches)
    
    # 查找API端点
    api_patterns = [
        r'["\']([^"\']*api[^"\']*)["\']',
        r'["\']([^"\']*video[^"\']*)["\']',
        r'["\']([^"\']*stream[^"\']*)["\']',
        r'["\']([^"\']*play[^"\']*)["\']',
    ]
    
    for pattern in api_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            if match.startswith('/'):
                full_url = urljoin(base_url, match)
            elif match.startswith('http'):
                full_url = match
            else:
                full_url = urljoin(base_url, match)
            
            if 'api' in full_url.lower() or 'video' in full_url.lower():
                ajax_info['api_endpoints'].append(full_url)
    
    # 去重
    ajax_info['api_endpoints'] = list(set(ajax_info['api_endpoints']))
    
    return ajax_info


def test_api_endpoint(url):
    """
    测试API端点
    
    Args:
        url: API端点URL
    
    Returns:
        测试结果
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://jptt.tv/',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return {
            'url': url,
            'status_code': response.status_code,
            'content_type': response.headers.get('content-type', ''),
            'content_length': len(response.text),
            'is_json': 'application/json' in response.headers.get('content-type', ''),
            'content_preview': response.text[:200] if response.text else ''
        }
    except Exception as e:
        return {
            'url': url,
            'error': str(e)
        }


def analyze_video_page_players(url):
    """
    分析视频页面的播放器配置
    
    Args:
        url: 视频页面URL
    
    Returns:
        播放器分析结果
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
        print(f"🔍 分析播放器配置: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        content = response.text
        
        analysis = {
            'url': url,
            'title': None,
            'jwplayer': analyze_jwplayer_config(content, url),
            'fluidplayer': analyze_fluidplayer_config(content, url),
            'ajax': analyze_ajax_requests(content, url),
            'all_video_sources': []
        }
        
        # 获取标题
        soup = BeautifulSoup(content, 'html.parser')
        title_tag = soup.find('title')
        if title_tag:
            analysis['title'] = title_tag.get_text().strip()
        
        # 收集所有视频源
        analysis['all_video_sources'].extend(analysis['jwplayer']['video_sources'])
        analysis['all_video_sources'].extend(analysis['fluidplayer']['video_sources'])
        
        # 去重
        analysis['all_video_sources'] = list(set(analysis['all_video_sources']))
        
        return analysis
        
    except Exception as e:
        return {
            'url': url,
            'error': str(e)
        }


def main():
    """主函数"""
    print("🎮 播放器配置分析器")
    print("=" * 60)
    
    # 读取之前保存的视频链接
    try:
        with open("video_pages_analysis.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        video_links = data['video_links']
        print(f"📄 读取到 {len(video_links)} 个视频链接")
        
        # 分析前3个视频页面的播放器配置
        print(f"\n🔍 分析前3个视频页面的播放器配置...")
        player_analyses = []
        
        for i, video_url in enumerate(video_links[:3], 1):
            print(f"\n--- 分析第 {i} 个视频的播放器 ---")
            analysis = analyze_video_page_players(video_url)
            player_analyses.append(analysis)
            
            if 'error' in analysis:
                print(f"❌ 分析失败: {analysis['error']}")
            else:
                print(f"✅ 分析成功")
                print(f"  标题: {analysis['title']}")
                print(f"  JWPlayer: {'是' if analysis['jwplayer']['has_jwplayer'] else '否'}")
                print(f"  FluidPlayer: {'是' if analysis['fluidplayer']['has_fluidplayer'] else '否'}")
                print(f"  AJAX请求数: {len(analysis['ajax']['ajax_requests'])}")
                print(f"  API端点数: {len(analysis['ajax']['api_endpoints'])}")
                print(f"  视频源数: {len(analysis['all_video_sources'])}")
                
                if analysis['all_video_sources']:
                    print(f"  视频源:")
                    for j, source in enumerate(analysis['all_video_sources'][:3], 1):
                        print(f"    {j}. {source}")
                    if len(analysis['all_video_sources']) > 3:
                        print(f"    ... 还有 {len(analysis['all_video_sources']) - 3} 个")
                
                if analysis['ajax']['api_endpoints']:
                    print(f"  API端点:")
                    for j, endpoint in enumerate(analysis['ajax']['api_endpoints'][:3], 1):
                        print(f"    {j}. {endpoint}")
                    if len(analysis['ajax']['api_endpoints']) > 3:
                        print(f"    ... 还有 {len(analysis['ajax']['api_endpoints']) - 3} 个")
            
            time.sleep(1)  # 避免请求过快
        
        # 测试API端点
        print(f"\n🧪 测试API端点...")
        all_api_endpoints = []
        for analysis in player_analyses:
            if 'ajax' in analysis and 'api_endpoints' in analysis['ajax']:
                all_api_endpoints.extend(analysis['ajax']['api_endpoints'])
        
        all_api_endpoints = list(set(all_api_endpoints))
        
        if all_api_endpoints:
            print(f"找到 {len(all_api_endpoints)} 个API端点，测试前5个...")
            api_test_results = []
            
            for i, endpoint in enumerate(all_api_endpoints[:5], 1):
                print(f"  测试API {i}: {endpoint}")
                test_result = test_api_endpoint(endpoint)
                api_test_results.append(test_result)
                
                if 'error' in test_result:
                    print(f"    ❌ 测试失败: {test_result['error']}")
                else:
                    print(f"    ✅ 状态码: {test_result['status_code']}")
                    print(f"    内容类型: {test_result['content_type']}")
                    print(f"    内容长度: {test_result['content_length']}")
                    if test_result['is_json']:
                        print(f"    JSON内容预览: {test_result['content_preview']}")
                
                time.sleep(1)
        else:
            print("未找到API端点")
            api_test_results = []
        
        # 保存分析结果
        result = {
            'player_analyses': player_analyses,
            'api_test_results': api_test_results,
            'summary': {
                'total_analyzed': len(player_analyses),
                'successful_analyses': len([a for a in player_analyses if 'error' not in a]),
                'total_video_sources': sum(len(a.get('all_video_sources', [])) for a in player_analyses),
                'total_api_endpoints': len(all_api_endpoints),
                'jwplayer_pages': len([a for a in player_analyses if a.get('jwplayer', {}).get('has_jwplayer', False)]),
                'fluidplayer_pages': len([a for a in player_analyses if a.get('fluidplayer', {}).get('has_fluidplayer', False)])
            }
        }
        
        with open("player_config_analysis.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 播放器配置分析结果已保存到: player_config_analysis.json")
        
        # 统计信息
        print(f"\n📊 播放器配置分析统计:")
        print(f"  分析的页面数: {result['summary']['total_analyzed']}")
        print(f"  成功分析的页面: {result['summary']['successful_analyses']}")
        print(f"  使用JWPlayer的页面: {result['summary']['jwplayer_pages']}")
        print(f"  使用FluidPlayer的页面: {result['summary']['fluidplayer_pages']}")
        print(f"  总视频源数: {result['summary']['total_video_sources']}")
        print(f"  总API端点数: {result['summary']['total_api_endpoints']}")
        
        # 显示所有找到的视频源
        all_video_sources = []
        for analysis in player_analyses:
            if 'all_video_sources' in analysis:
                all_video_sources.extend(analysis['all_video_sources'])
        
        all_video_sources = list(set(all_video_sources))
        
        if all_video_sources:
            print(f"\n🎬 所有找到的视频源:")
            for i, source in enumerate(all_video_sources, 1):
                print(f"{i:2d}. {source}")
        else:
            print(f"\n❌ 未找到视频源")
        
    except FileNotFoundError:
        print("❌ 未找到 video_pages_analysis.json 文件")
        print("请先运行 video_page_extractor.py")
    except Exception as e:
        print(f"❌ 处理失败: {e}")
    
    print(f"\n🎉 播放器配置分析完成!")


if __name__ == "__main__":
    main()
