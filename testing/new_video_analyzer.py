#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新视频链接分析器
分析新解密出的视频链接
"""

import re
import json
import requests
from urllib.parse import urlparse, unquote


def extract_clean_video_url(js_code):
    """
    精确提取视频URL，去除多余的字符
    
    Args:
        js_code: JavaScript代码字符串
    
    Returns:
        清理后的视频URL
    """
    # 更精确的正则表达式来匹配视频URL
    url_pattern = r"url:\s*'([^']+\.m3u8[^']*)'"
    match = re.search(url_pattern, js_code)
    
    if match:
        video_url = match.group(1)
        # 清理URL，去除可能的转义字符
        video_url = video_url.replace('\\', '')
        return video_url
    
    return None


def get_m3u8_content(url):
    """
    获取M3U8文件内容
    
    Args:
        url: M3U8文件URL
    
    Returns:
        M3U8文件内容
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.a3m5m.com/',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        return response.text
    except Exception as e:
        print(f"获取M3U8内容失败: {e}")
        return None


def parse_m3u8_content(content, base_url):
    """
    解析M3U8内容，提取视频片段链接
    
    Args:
        content: M3U8文件内容
        base_url: 基础URL
    
    Returns:
        视频片段链接列表
    """
    if not content:
        return []
    
    video_segments = []
    lines = content.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        # 跳过注释和空行
        if line.startswith('#') or not line:
            continue
        
        # 如果是相对路径，转换为绝对路径
        if line.startswith('/'):
            # 绝对路径
            parsed_base = urlparse(base_url)
            full_url = f"{parsed_base.scheme}://{parsed_base.netloc}{line}"
        elif line.startswith('http'):
            # 已经是完整URL
            full_url = line
        else:
            # 相对路径
            base_path = '/'.join(base_url.split('/')[:-1])
            full_url = f"{base_path}/{line}"
        
        video_segments.append(full_url)
    
    return video_segments


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
            'Referer': 'https://www.a3m5m.com/',
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
    print("🎬 新视频链接分析器")
    print("=" * 60)
    
    # 解密后的JavaScript代码
    js_code = """if(-1!=='mugua16.cfd,mugua22.cfd,mugua26.cfd,mugua50.cfd,mugua55.cfd,mugua95.cfd,mugua15.cfd,mugua25.cfd,mugua52.cfd,mugua92.cfd,mugua23.cfd,mugua12.cfd,91quanji.com,mugua17.cfd,mugua62.cfd,mugua78.cfd'.indexOf(window.location.hostname)){const dp = new DPlayer({container: document.getElementById('dplayer'),lang: 'zh-cn',video: {url: 'https://8015.o9hx3f-s8jamrmtps5.sbs/9/04/ff/91/e2fda9794729372dca7f165d1d/chunklist_w.m3u8?v=1759637531-IA%2BpS7sjHg3qZObmry0HzkvfxJC8rSqJlFAaByY1pbw%3D',type: 'auto'},theme:'#ff0046',autoplay:true});if(/mobile/i.test(window.navigator.userAgent)){dp.template.videoWrap.addEventListener('click',function(){if(dp.video.paused){dp.play();}if(dp.controller.isShow()){dp.controller.setAutoHide();}});dp.on('play',function(){dp.controller.setAutoHide();});dp.on('pause',function(){dp.controller.setAutoHide();});}$('.dplayer-icon.dplayer-full-icon').removeAttr('data-balloon');}"""
    
    print("📄 分析新的JavaScript代码...")
    print(f"代码长度: {len(js_code)} 字符")
    
    # 提取清理后的视频URL
    video_url = extract_clean_video_url(js_code)
    
    if video_url:
        print(f"\n✅ 找到新的视频链接:")
        print(f"🎬 {video_url}")
        
        # 解析URL信息
        parsed = urlparse(video_url)
        print(f"\n📊 URL信息:")
        print(f"  协议: {parsed.scheme}")
        print(f"  域名: {parsed.netloc}")
        print(f"  路径: {parsed.path}")
        print(f"  查询参数: {parsed.query}")
        
        # 测试链接可访问性
        print(f"\n🧪 测试链接可访问性...")
        test_result = test_video_link(video_url)
        
        if test_result.get('accessible'):
            print(f"✅ 链接可访问!")
            print(f"  状态码: {test_result['status_code']}")
            print(f"  内容类型: {test_result['content_type']}")
            if test_result['content_length']:
                print(f"  内容长度: {test_result['content_length']} 字节")
        else:
            print(f"❌ 链接不可访问")
            if 'error' in test_result:
                print(f"  错误: {test_result['error']}")
            else:
                print(f"  状态码: {test_result.get('status_code', 'Unknown')}")
        
        # 获取M3U8内容
        print(f"\n📥 获取M3U8播放列表...")
        m3u8_content = get_m3u8_content(video_url)
        
        if m3u8_content:
            print(f"✅ 成功获取M3U8内容")
            print(f"内容长度: {len(m3u8_content)} 字符")
            
            # 保存M3U8内容
            with open("new_playlist.m3u8", "w", encoding="utf-8") as f:
                f.write(m3u8_content)
            print(f"💾 M3U8内容已保存到: new_playlist.m3u8")
            
            # 解析M3U8内容
            print(f"\n🔍 解析M3U8播放列表...")
            video_segments = parse_m3u8_content(m3u8_content, video_url)
            
            if video_segments:
                print(f"✅ 找到 {len(video_segments)} 个视频片段:")
                print("-" * 60)
                
                for i, segment in enumerate(video_segments[:10], 1):  # 只显示前10个
                    print(f"{i:2d}. {segment}")
                
                if len(video_segments) > 10:
                    print(f"... 还有 {len(video_segments) - 10} 个片段")
                
                # 保存所有视频片段链接
                with open("new_video_segments.txt", "w", encoding="utf-8") as f:
                    for segment in video_segments:
                        f.write(f"{segment}\n")
                print(f"\n💾 所有视频片段链接已保存到: new_video_segments.txt")
                
                # 创建完整的结果报告
                result = {
                    'main_m3u8_url': video_url,
                    'm3u8_content': m3u8_content,
                    'video_segments': video_segments,
                    'total_segments': len(video_segments),
                    'domain': parsed.netloc,
                    'path': parsed.path,
                    'query_params': parsed.query,
                    'test_result': test_result
                }
                
                with open("new_complete_video_analysis.json", "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                print(f"💾 完整分析结果已保存到: new_complete_video_analysis.json")
                
            else:
                print("❌ 未找到视频片段")
        else:
            print("❌ 获取M3U8内容失败")
    else:
        print("❌ 未找到视频链接")
    
    print(f"\n🎉 新视频链接分析完成!")
    if video_url:
        print(f"🎬 新的视频链接: {video_url}")
        print(f"📱 这是一个HLS流媒体链接，可以在支持HLS的播放器中播放")
        print(f"🔗 推荐使用VLC、PotPlayer等播放器打开此链接")
        
        # 比较两个视频链接
        print(f"\n🔄 与之前的视频链接对比:")
        old_url = "https://8015.o9hx3f-s8jamrmtps5.sbs/0/e6/79/4f/1a384e695c7e5553b2ea13aa7a/chunklist_w.m3u8?v=1759636368-0pRDFVkKkavLBTJomTSSt%2FAHGk3fZLHdwZExioNukUM%3D"
        print(f"  旧链接: {old_url}")
        print(f"  新链接: {video_url}")
        
        if old_url != video_url:
            print(f"  ✅ 这是两个不同的视频链接")
            print(f"  📊 路径不同: 旧链接路径包含 '0/e6/79/4f'，新链接路径包含 '9/04/ff/91'")
            print(f"  🔑 签名不同: 两个链接的签名参数不同")
        else:
            print(f"  ⚠️  这是相同的视频链接")


if __name__ == "__main__":
    main()
