#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频链接提取器
从解密后的JavaScript代码中提取视频链接
"""

import re
import json
import requests
from urllib.parse import urlparse, unquote


def extract_video_links(js_code):
    """
    从JavaScript代码中提取视频链接
    
    Args:
        js_code: JavaScript代码字符串
    
    Returns:
        提取到的视频链接列表
    """
    video_links = []
    
    # 查找M3U8链接
    m3u8_pattern = r'https?://[^"\s<>]+\.m3u8[^"\s<>]*'
    m3u8_matches = re.findall(m3u8_pattern, js_code, re.IGNORECASE)
    video_links.extend(m3u8_matches)
    
    # 查找MP4链接
    mp4_pattern = r'https?://[^"\s<>]+\.mp4[^"\s<>]*'
    mp4_matches = re.findall(mp4_pattern, js_code, re.IGNORECASE)
    video_links.extend(mp4_matches)
    
    # 查找其他视频格式
    other_video_pattern = r'https?://[^"\s<>]+\.(webm|avi|mov|flv|mkv|ts)[^"\s<>]*'
    other_matches = re.findall(other_video_pattern, js_code, re.IGNORECASE)
    video_links.extend(other_matches)
    
    # 去重
    video_links = list(set(video_links))
    
    return video_links


def analyze_video_link(url):
    """
    分析视频链接
    
    Args:
        url: 视频链接
    
    Returns:
        分析结果字典
    """
    result = {
        'url': url,
        'domain': '',
        'type': '',
        'parameters': {},
        'is_valid': False
    }
    
    try:
        # 解析URL
        parsed = urlparse(url)
        result['domain'] = parsed.netloc
        result['is_valid'] = True
        
        # 判断视频类型
        if '.m3u8' in url.lower():
            result['type'] = 'HLS (HTTP Live Streaming)'
        elif '.mp4' in url.lower():
            result['type'] = 'MP4'
        elif '.webm' in url.lower():
            result['type'] = 'WebM'
        elif '.ts' in url.lower():
            result['type'] = 'Transport Stream'
        else:
            result['type'] = 'Unknown'
        
        # 解析查询参数
        if parsed.query:
            params = {}
            for param in parsed.query.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = unquote(value)
            result['parameters'] = params
        
    except Exception as e:
        result['error'] = str(e)
    
    return result


def test_video_link(url):
    """
    测试视频链接是否可访问
    
    Args:
        url: 视频链接
    
    Returns:
        测试结果
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        response = requests.head(url, headers=headers, timeout=10)
        return {
            'status_code': response.status_code,
            'accessible': response.status_code == 200,
            'content_type': response.headers.get('content-type', ''),
            'content_length': response.headers.get('content-length', ''),
        }
    except Exception as e:
        return {
            'error': str(e),
            'accessible': False
        }


def main():
    """主函数"""
    print("🎬 视频链接提取器")
    print("=" * 60)
    
    # 解密后的JavaScript代码
    js_code = """if(-1!=='mugua16.cfd,mugua22.cfd,mugua26.cfd,mugua50.cfd,mugua55.cfd,mugua95.cfd,mugua15.cfd,mugua25.cfd,mugua52.cfd,mugua92.cfd,mugua23.cfd,mugua12.cfd,91quanji.com,mugua17.cfd,mugua62.cfd,mugua78.cfd'.indexOf(window.location.hostname)){const dp = new DPlayer({container: document.getElementById('dplayer'),lang: 'zh-cn',video: {url: 'https://8015.o9hx3f-s8jamrmtps5.sbs/0/e6/79/4f/1a384e695c7e5553b2ea13aa7a/chunklist_w.m3u8?v=1759636368-0pRDFVkKkavLBTJomTSSt%2FAHGk3fZLHdwZExioNukUM%3D',type: 'auto'},theme:'#ff0046',autoplay:true});if(/mobile/i.test(window.navigator.userAgent)){dp.template.videoWrap.addEventListener('click',function(){if(dp.video.paused){dp.play();}if(dp.controller.isShow()){dp.controller.setAutoHide();}});dp.on('play',function(){dp.controller.setAutoHide();});dp.on('pause',function(){dp.controller.setAutoHide();});}$('.dplayer-icon.dplayer-full-icon').removeAttr('data-balloon');}"""
    
    print("📄 分析JavaScript代码...")
    print(f"代码长度: {len(js_code)} 字符")
    
    # 提取视频链接
    video_links = extract_video_links(js_code)
    
    print(f"\n🎯 找到 {len(video_links)} 个视频链接:")
    print("-" * 60)
    
    for i, link in enumerate(video_links, 1):
        print(f"\n{i}. 视频链接: {link}")
        
        # 分析链接
        analysis = analyze_video_link(link)
        print(f"   域名: {analysis['domain']}")
        print(f"   类型: {analysis['type']}")
        
        if analysis['parameters']:
            print(f"   参数: {analysis['parameters']}")
        
        # 测试链接
        print("   测试链接可访问性...")
        test_result = test_video_link(link)
        
        if test_result.get('accessible'):
            print(f"   ✅ 链接可访问 (状态码: {test_result['status_code']})")
            print(f"   内容类型: {test_result['content_type']}")
            if test_result['content_length']:
                print(f"   内容长度: {test_result['content_length']} 字节")
        else:
            print(f"   ❌ 链接不可访问")
            if 'error' in test_result:
                print(f"   错误: {test_result['error']}")
            else:
                print(f"   状态码: {test_result.get('status_code', 'Unknown')}")
    
    # 提取播放器配置信息
    print(f"\n🎮 播放器配置信息:")
    print("-" * 60)
    
    # 提取DPlayer配置
    dp_config_match = re.search(r'new DPlayer\(\{([^}]+)\}', js_code)
    if dp_config_match:
        config_text = dp_config_match.group(1)
        print("DPlayer配置:")
        print(f"  {config_text}")
    
    # 提取视频URL
    video_url_match = re.search(r"url:\s*'([^']+)'", js_code)
    if video_url_match:
        video_url = video_url_match.group(1)
        print(f"\n🎬 主要视频链接:")
        print(f"  {video_url}")
        
        # 分析主要视频链接
        main_analysis = analyze_video_link(video_url)
        print(f"\n📊 详细分析:")
        print(f"  完整URL: {main_analysis['url']}")
        print(f"  域名: {main_analysis['domain']}")
        print(f"  类型: {main_analysis['type']}")
        
        if main_analysis['parameters']:
            print(f"  查询参数:")
            for key, value in main_analysis['parameters'].items():
                print(f"    {key}: {value}")
        
        # 测试主要视频链接
        print(f"\n🧪 测试主要视频链接...")
        main_test = test_video_link(video_url)
        
        if main_test.get('accessible'):
            print(f"  ✅ 视频链接可访问!")
            print(f"  状态码: {main_test['status_code']}")
            print(f"  内容类型: {main_test['content_type']}")
            if main_test['content_length']:
                print(f"  内容长度: {main_test['content_length']} 字节")
        else:
            print(f"  ❌ 视频链接不可访问")
            if 'error' in main_test:
                print(f"  错误: {main_test['error']}")
    
    # 保存结果
    result = {
        'video_links': video_links,
        'main_video_url': video_url_match.group(1) if video_url_match else None,
        'analysis': [analyze_video_link(link) for link in video_links],
        'test_results': [test_video_link(link) for link in video_links]
    }
    
    with open("video_links_analysis.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 分析结果已保存到: video_links_analysis.json")
    
    print(f"\n🎉 视频链接提取完成!")
    if video_links:
        print(f"✅ 成功找到 {len(video_links)} 个视频链接")
        print(f"🎬 主要视频链接: {video_links[0]}")
    else:
        print("❌ 未找到视频链接")


if __name__ == "__main__":
    main()
