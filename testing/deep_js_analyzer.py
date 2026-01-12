#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度JavaScript分析器
深入分析视频页面的JavaScript代码，查找加密的视频链接
"""

import requests
import json
import re
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


def decrypt_xor(encrypted_text, key=128):
    """
    XOR解密函数
    """
    decrypted = ""
    for char in encrypted_text:
        char_code = ord(char)
        decrypted_char_code = key ^ char_code
        decrypted += chr(decrypted_char_code)
    return decrypted


def extract_js_files(content, base_url):
    """
    提取页面中的JavaScript文件链接
    
    Args:
        content: 页面内容
        base_url: 基础URL
    
    Returns:
        JavaScript文件链接列表
    """
    soup = BeautifulSoup(content, 'html.parser')
    js_files = []
    
    # 查找script标签
    script_tags = soup.find_all('script', src=True)
    for script in script_tags:
        src = script.get('src')
        if src:
            if src.startswith('/'):
                full_url = urljoin(base_url, src)
            elif src.startswith('http'):
                full_url = src
            else:
                full_url = urljoin(base_url, src)
            js_files.append(full_url)
    
    return js_files


def analyze_js_content(js_content, url):
    """
    分析JavaScript内容，查找加密代码和视频链接
    
    Args:
        js_content: JavaScript内容
        url: JavaScript文件URL
    
    Returns:
        分析结果
    """
    analysis = {
        'url': url,
        'has_encrypted_code': False,
        'encrypted_functions': [],
        'video_links': [],
        'm3u8_links': [],
        'api_endpoints': [],
        'dplayer_configs': []
    }
    
    # 查找加密的eval函数调用
    eval_pattern = r'eval\s*\(\s*I\s*\(\s*["\']([^"\']+)["\']\s*\)\s*\)'
    eval_matches = re.findall(eval_pattern, js_content)
    
    if eval_matches:
        analysis['has_encrypted_code'] = True
        for encrypted_text in eval_matches:
            try:
                decrypted = decrypt_xor(encrypted_text, 128)
                analysis['encrypted_functions'].append({
                    'encrypted': encrypted_text,
                    'decrypted': decrypted
                })
                
                # 在解密后的代码中查找视频链接
                video_patterns = [
                    r'https?://[^"\s<>]+\.m3u8[^"\s<>]*',
                    r'https?://[^"\s<>]+\.mp4[^"\s<>]*',
                    r'https?://[^"\s<>]+\.(webm|avi|mov|flv|mkv|ts)[^"\s<>]*'
                ]
                
                for pattern in video_patterns:
                    matches = re.findall(pattern, decrypted, re.IGNORECASE)
                    analysis['video_links'].extend(matches)
                
            except Exception as e:
                print(f"解密失败: {e}")
    
    # 直接查找视频链接
    video_patterns = [
        r'https?://[^"\s<>]+\.m3u8[^"\s<>]*',
        r'https?://[^"\s<>]+\.mp4[^"\s<>]*',
        r'https?://[^"\s<>]+\.(webm|avi|mov|flv|mkv|ts)[^"\s<>]*'
    ]
    
    for pattern in video_patterns:
        matches = re.findall(pattern, js_content, re.IGNORECASE)
        analysis['video_links'].extend(matches)
    
    # 查找API端点
    api_pattern = r'https?://[^"\s<>]*api[^"\s<>]*'
    api_matches = re.findall(api_pattern, js_content, re.IGNORECASE)
    analysis['api_endpoints'].extend(api_matches)
    
    # 查找DPlayer配置
    dplayer_pattern = r'new\s+DPlayer\s*\(\s*\{[^}]+\}'
    dplayer_matches = re.findall(dplayer_pattern, js_content, re.IGNORECASE | re.DOTALL)
    analysis['dplayer_configs'].extend(dplayer_matches)
    
    # 去重
    analysis['video_links'] = list(set(analysis['video_links']))
    analysis['m3u8_links'] = [link for link in analysis['video_links'] if '.m3u8' in link]
    analysis['api_endpoints'] = list(set(analysis['api_endpoints']))
    
    return analysis


def fetch_js_file(url):
    """
    获取JavaScript文件内容
    
    Args:
        url: JavaScript文件URL
    
    Returns:
        JavaScript文件内容
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://jptt.tv/',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"获取JS文件失败 {url}: {e}")
        return None


def analyze_video_page_deep(url):
    """
    深度分析视频页面
    
    Args:
        url: 视频页面URL
    
    Returns:
        深度分析结果
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
        print(f"🔍 深度分析视频页面: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        analysis = {
            'url': url,
            'title': None,
            'js_files': [],
            'js_analyses': [],
            'encrypted_functions': [],
            'all_video_links': [],
            'all_m3u8_links': [],
            'status_code': response.status_code
        }
        
        # 获取标题
        title_tag = soup.find('title')
        if title_tag:
            analysis['title'] = title_tag.get_text().strip()
        
        # 提取JavaScript文件
        js_files = extract_js_files(response.text, url)
        analysis['js_files'] = js_files
        
        print(f"  找到 {len(js_files)} 个JavaScript文件")
        
        # 分析每个JavaScript文件
        for js_url in js_files:
            print(f"    分析JS文件: {js_url}")
            js_content = fetch_js_file(js_url)
            
            if js_content:
                js_analysis = analyze_js_content(js_content, js_url)
                analysis['js_analyses'].append(js_analysis)
                
                # 收集所有视频链接
                analysis['all_video_links'].extend(js_analysis['video_links'])
                analysis['all_m3u8_links'].extend(js_analysis['m3u8_links'])
                analysis['encrypted_functions'].extend(js_analysis['encrypted_functions'])
                
                if js_analysis['has_encrypted_code']:
                    print(f"      ✅ 找到加密代码")
                if js_analysis['video_links']:
                    print(f"      ✅ 找到 {len(js_analysis['video_links'])} 个视频链接")
            
            time.sleep(0.5)  # 避免请求过快
        
        # 去重
        analysis['all_video_links'] = list(set(analysis['all_video_links']))
        analysis['all_m3u8_links'] = list(set(analysis['all_m3u8_links']))
        
        return analysis
        
    except Exception as e:
        return {
            'url': url,
            'error': str(e),
            'status_code': getattr(e, 'response', {}).get('status_code', None) if hasattr(e, 'response') else None
        }


def main():
    """主函数"""
    print("🔍 深度JavaScript分析器")
    print("=" * 60)
    
    # 读取之前保存的视频链接
    try:
        with open("video_pages_analysis.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        video_links = data['video_links']
        print(f"📄 读取到 {len(video_links)} 个视频链接")
        
        # 深度分析前3个视频页面
        print(f"\n🔍 深度分析前3个视频页面...")
        deep_analyses = []
        
        for i, video_url in enumerate(video_links[:3], 1):
            print(f"\n--- 深度分析第 {i} 个视频 ---")
            analysis = analyze_video_page_deep(video_url)
            deep_analyses.append(analysis)
            
            if 'error' in analysis:
                print(f"❌ 分析失败: {analysis['error']}")
            else:
                print(f"✅ 分析成功")
                print(f"  标题: {analysis['title']}")
                print(f"  JS文件数: {len(analysis['js_files'])}")
                print(f"  加密函数数: {len(analysis['encrypted_functions'])}")
                print(f"  视频链接数: {len(analysis['all_video_links'])}")
                print(f"  M3U8链接数: {len(analysis['all_m3u8_links'])}")
                
                if analysis['all_video_links']:
                    print(f"  视频链接:")
                    for j, vlink in enumerate(analysis['all_video_links'][:3], 1):
                        print(f"    {j}. {vlink}")
                    if len(analysis['all_video_links']) > 3:
                        print(f"    ... 还有 {len(analysis['all_video_links']) - 3} 个")
                
                if analysis['encrypted_functions']:
                    print(f"  加密函数:")
                    for j, func in enumerate(analysis['encrypted_functions'][:2], 1):
                        print(f"    {j}. 解密后: {func['decrypted'][:100]}...")
                        # 在解密后的代码中查找视频链接
                        video_pattern = r'https?://[^"\s<>]+\.m3u8[^"\s<>]*'
                        matches = re.findall(video_pattern, func['decrypted'], re.IGNORECASE)
                        if matches:
                            print(f"       找到M3U8链接: {matches[0]}")
            
            time.sleep(2)  # 避免请求过快
        
        # 保存深度分析结果
        result = {
            'deep_analyses': deep_analyses,
            'summary': {
                'total_analyzed': len(deep_analyses),
                'successful_analyses': len([a for a in deep_analyses if 'error' not in a]),
                'total_video_links': sum(len(a.get('all_video_links', [])) for a in deep_analyses),
                'total_m3u8_links': sum(len(a.get('all_m3u8_links', [])) for a in deep_analyses),
                'total_encrypted_functions': sum(len(a.get('encrypted_functions', [])) for a in deep_analyses)
            }
        }
        
        with open("deep_js_analysis.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 深度分析结果已保存到: deep_js_analysis.json")
        
        # 统计信息
        print(f"\n📊 深度分析统计:")
        print(f"  分析的页面数: {result['summary']['total_analyzed']}")
        print(f"  成功分析的页面: {result['summary']['successful_analyses']}")
        print(f"  总视频链接数: {result['summary']['total_video_links']}")
        print(f"  总M3U8链接数: {result['summary']['total_m3u8_links']}")
        print(f"  总加密函数数: {result['summary']['total_encrypted_functions']}")
        
        # 显示所有找到的视频链接
        all_video_links = []
        for analysis in deep_analyses:
            if 'all_video_links' in analysis:
                all_video_links.extend(analysis['all_video_links'])
        
        all_video_links = list(set(all_video_links))
        
        if all_video_links:
            print(f"\n🎬 所有找到的视频链接:")
            for i, link in enumerate(all_video_links, 1):
                print(f"{i:2d}. {link}")
        
    except FileNotFoundError:
        print("❌ 未找到 video_pages_analysis.json 文件")
        print("请先运行 video_page_extractor.py")
    except Exception as e:
        print(f"❌ 处理失败: {e}")
    
    print(f"\n🎉 深度JavaScript分析完成!")


if __name__ == "__main__":
    main()
