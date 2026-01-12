#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重定向分析器
分析HTML重定向页面并获取目标页面内容
"""

import requests
import time
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup


def analyze_redirect_html(html_content):
    """
    分析HTML重定向页面
    
    Args:
        html_content: HTML内容
    
    Returns:
        重定向信息字典
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    redirect_info = {
        'meta_refresh': None,
        'redirect_url': None,
        'redirect_delay': 0,
        'title': None,
        'cloudflare_script': False
    }
    
    # 获取标题
    title_tag = soup.find('title')
    if title_tag:
        redirect_info['title'] = title_tag.get_text().strip()
    
    # 查找meta refresh标签
    meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
    if meta_refresh:
        content = meta_refresh.get('content', '')
        redirect_info['meta_refresh'] = content
        
        # 解析重定向URL和延迟时间
        if 'url=' in content:
            parts = content.split('url=', 1)
            if len(parts) == 2:
                redirect_info['redirect_delay'] = int(parts[0].split(';')[0]) if parts[0] else 0
                redirect_info['redirect_url'] = parts[1].strip("'\"")
    
    # 查找链接
    link_tag = soup.find('a')
    if link_tag and link_tag.get('href'):
        redirect_info['redirect_url'] = link_tag.get('href')
    
    # 检查是否有Cloudflare脚本
    cloudflare_script = soup.find('script', attrs={'src': lambda x: x and 'cloudflareinsights.com' in x})
    if cloudflare_script:
        redirect_info['cloudflare_script'] = True
    
    return redirect_info


def follow_redirect(url, max_redirects=5):
    """
    跟随重定向并获取最终页面内容
    
    Args:
        url: 起始URL
        max_redirects: 最大重定向次数
    
    Returns:
        重定向链和最终内容
    """
    redirect_chain = []
    current_url = url
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    for i in range(max_redirects):
        try:
            print(f"🔄 第 {i+1} 次请求: {current_url}")
            
            response = requests.get(current_url, headers=headers, timeout=10, allow_redirects=False)
            redirect_chain.append({
                'url': current_url,
                'status_code': response.status_code,
                'headers': dict(response.headers)
            })
            
            print(f"   状态码: {response.status_code}")
            
            # 如果是重定向状态码
            if response.status_code in [301, 302, 303, 307, 308]:
                location = response.headers.get('Location')
                if location:
                    # 处理相对URL
                    if location.startswith('//'):
                        location = 'https:' + location
                    elif location.startswith('/'):
                        parsed = urlparse(current_url)
                        location = f"{parsed.scheme}://{parsed.netloc}{location}"
                    elif not location.startswith('http'):
                        location = urljoin(current_url, location)
                    
                    print(f"   重定向到: {location}")
                    current_url = location
                    time.sleep(1)  # 避免请求过快
                    continue
            
            # 如果不是重定向，返回内容
            return {
                'redirect_chain': redirect_chain,
                'final_url': current_url,
                'final_content': response.text,
                'final_status_code': response.status_code,
                'final_headers': dict(response.headers)
            }
            
        except Exception as e:
            print(f"❌ 请求失败: {e}")
            return {
                'redirect_chain': redirect_chain,
                'error': str(e),
                'final_url': current_url
            }
    
    print(f"⚠️ 达到最大重定向次数 ({max_redirects})")
    return {
        'redirect_chain': redirect_chain,
        'final_url': current_url,
        'error': 'Max redirects exceeded'
    }


def analyze_final_page(content, url):
    """
    分析最终页面内容
    
    Args:
        content: 页面内容
        url: 页面URL
    
    Returns:
        页面分析结果
    """
    soup = BeautifulSoup(content, 'html.parser')
    
    analysis = {
        'url': url,
        'title': None,
        'meta_description': None,
        'video_links': [],
        'image_links': [],
        'script_sources': [],
        'has_video_player': False,
        'has_cloudflare': False,
        'page_type': 'unknown'
    }
    
    # 获取标题
    title_tag = soup.find('title')
    if title_tag:
        analysis['title'] = title_tag.get_text().strip()
    
    # 获取meta描述
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc:
        analysis['meta_description'] = meta_desc.get('content', '').strip()
    
    # 查找视频链接
    video_patterns = [
        r'https?://[^"\s<>]+\.(m3u8|mp4|webm|avi|mov|flv|mkv|ts)[^"\s<>]*',
        r'https?://[^"\s<>]*video[^"\s<>]*',
        r'https?://[^"\s<>]*stream[^"\s<>]*'
    ]
    
    import re
    for pattern in video_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        analysis['video_links'].extend(matches)
    
    # 去重
    analysis['video_links'] = list(set(analysis['video_links']))
    
    # 查找图片链接
    img_tags = soup.find_all('img')
    for img in img_tags:
        src = img.get('src')
        if src:
            analysis['image_links'].append(src)
    
    # 查找脚本源
    script_tags = soup.find_all('script', src=True)
    for script in script_tags:
        src = script.get('src')
        if src:
            analysis['script_sources'].append(src)
            if 'cloudflare' in src.lower():
                analysis['has_cloudflare'] = True
    
    # 检查是否有视频播放器
    video_indicators = ['video', 'player', 'dplayer', 'hls', 'm3u8', 'mp4']
    content_lower = content.lower()
    for indicator in video_indicators:
        if indicator in content_lower:
            analysis['has_video_player'] = True
            break
    
    # 判断页面类型
    if 'list' in url.lower():
        analysis['page_type'] = 'list_page'
    elif 'video' in url.lower() or analysis['has_video_player']:
        analysis['page_type'] = 'video_page'
    elif 'index' in url.lower() or 'home' in url.lower():
        analysis['page_type'] = 'home_page'
    
    return analysis


def main():
    """主函数"""
    print("🔄 重定向分析器")
    print("=" * 60)
    
    # 提供的HTML内容
    html_content = """<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8" />
        <meta http-equiv="refresh" content="0;url='//jptt.tv/list?idx=2&amp;sort=2'" />

        <title>Redirecting to //jptt.tv/list?idx=2&amp;sort=2</title>
    </head>
    <body>
        Redirecting to <a href="//jptt.tv/list?idx=2&amp;sort=2">//jptt.tv/list?idx=2&amp;sort=2</a>.
    <script defer src="https://static.cloudflareinsights.com/beacon.min.js/vcd15cbe7772f49c399c6a5babf22c1241717689176015" integrity="sha512-ZpsOmlRQV6y907TI0dKBHq9Md29nnaEIPlkf84rnaERnq6zvWvPUqr2ft8M1aS28oN72PdrCzSjY4U6VaAw1EQ==" data-cf-beacon='{"version":"2024.11.0","token":"9bce1cb6123f47babeabf08513dbfcc7","r":1,"server_timing":{"name":{"cfCacheStatus":true,"cfEdge":true,"cfExtPri":true,"cfL4":true,"cfOrigin":true,"cfSpeedBrain":true},"location_startswith":null}}' crossorigin="anonymous"></script>
</body>
</html>"""
    
    print("📄 分析HTML重定向页面...")
    
    # 分析重定向信息
    redirect_info = analyze_redirect_html(html_content)
    
    print(f"📊 重定向信息:")
    print(f"  标题: {redirect_info['title']}")
    print(f"  Meta刷新: {redirect_info['meta_refresh']}")
    print(f"  重定向URL: {redirect_info['redirect_url']}")
    print(f"  重定向延迟: {redirect_info['redirect_delay']} 秒")
    print(f"  Cloudflare脚本: {'是' if redirect_info['cloudflare_script'] else '否'}")
    
    if redirect_info['redirect_url']:
        # 处理相对URL
        target_url = redirect_info['redirect_url']
        if target_url.startswith('//'):
            target_url = 'https:' + target_url
        
        print(f"\n🎯 目标URL: {target_url}")
        
        # 跟随重定向
        print(f"\n🔄 跟随重定向...")
        result = follow_redirect(target_url)
        
        if 'error' in result:
            print(f"❌ 重定向失败: {result['error']}")
        else:
            print(f"\n✅ 重定向完成!")
            print(f"最终URL: {result['final_url']}")
            print(f"最终状态码: {result['final_status_code']}")
            
            # 分析最终页面
            if 'final_content' in result:
                print(f"\n🔍 分析最终页面...")
                page_analysis = analyze_final_page(result['final_content'], result['final_url'])
                
                print(f"📊 页面分析结果:")
                print(f"  标题: {page_analysis['title']}")
                print(f"  页面类型: {page_analysis['page_type']}")
                print(f"  描述: {page_analysis['meta_description']}")
                print(f"  视频播放器: {'是' if page_analysis['has_video_player'] else '否'}")
                print(f"  Cloudflare: {'是' if page_analysis['has_cloudflare'] else '否'}")
                print(f"  脚本数量: {len(page_analysis['script_sources'])}")
                print(f"  图片数量: {len(page_analysis['image_links'])}")
                print(f"  视频链接数量: {len(page_analysis['video_links'])}")
                
                if page_analysis['video_links']:
                    print(f"\n🎬 找到的视频链接:")
                    for i, link in enumerate(page_analysis['video_links'][:5], 1):
                        print(f"  {i}. {link}")
                    if len(page_analysis['video_links']) > 5:
                        print(f"  ... 还有 {len(page_analysis['video_links']) - 5} 个")
                
                # 保存结果
                import json
                full_result = {
                    'redirect_info': redirect_info,
                    'redirect_result': result,
                    'page_analysis': page_analysis
                }
                
                with open("redirect_analysis_result.json", "w", encoding="utf-8") as f:
                    json.dump(full_result, f, ensure_ascii=False, indent=2)
                
                print(f"\n💾 完整分析结果已保存到: redirect_analysis_result.json")
                
                # 保存最终页面内容
                with open("final_page_content.html", "w", encoding="utf-8") as f:
                    f.write(result['final_content'])
                print(f"💾 最终页面内容已保存到: final_page_content.html")
    
    print(f"\n🎉 重定向分析完成!")


if __name__ == "__main__":
    main()
