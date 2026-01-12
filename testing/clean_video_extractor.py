#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理视频链接提取器
精确提取完整的视频链接
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
    # 匹配 url: '...' 格式
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


def main():
    """主函数"""
    print("🎬 清理视频链接提取器")
    print("=" * 60)
    
    # 解密后的JavaScript代码
    js_code = """if(-1!=='mugua16.cfd,mugua22.cfd,mugua26.cfd,mugua50.cfd,mugua55.cfd,mugua95.cfd,mugua15.cfd,mugua25.cfd,mugua52.cfd,mugua92.cfd,mugua23.cfd,mugua12.cfd,91quanji.com,mugua17.cfd,mugua62.cfd,mugua78.cfd'.indexOf(window.location.hostname)){const dp = new DPlayer({container: document.getElementById('dplayer'),lang: 'zh-cn',video: {url: 'https://8015.o9hx3f-s8jamrmtps5.sbs/0/e6/79/4f/1a384e695c7e5553b2ea13aa7a/chunklist_w.m3u8?v=1759636368-0pRDFVkKkavLBTJomTSSt%2FAHGk3fZLHdwZExioNukUM%3D',type: 'auto'},theme:'#ff0046',autoplay:true});if(/mobile/i.test(window.navigator.userAgent)){dp.template.videoWrap.addEventListener('click',function(){if(dp.video.paused){dp.play();}if(dp.controller.isShow()){dp.controller.setAutoHide();}});dp.on('play',function(){dp.controller.setAutoHide();});dp.on('pause',function(){dp.controller.setAutoHide();});}$('.dplayer-icon.dplayer-full-icon').removeAttr('data-balloon');}"""
    
    print("📄 提取视频链接...")
    
    # 提取清理后的视频URL
    video_url = extract_clean_video_url(js_code)
    
    if video_url:
        print(f"✅ 找到视频链接:")
        print(f"🎬 {video_url}")
        
        # 解析URL信息
        parsed = urlparse(video_url)
        print(f"\n📊 URL信息:")
        print(f"  协议: {parsed.scheme}")
        print(f"  域名: {parsed.netloc}")
        print(f"  路径: {parsed.path}")
        print(f"  查询参数: {parsed.query}")
        
        # 获取M3U8内容
        print(f"\n📥 获取M3U8播放列表...")
        m3u8_content = get_m3u8_content(video_url)
        
        if m3u8_content:
            print(f"✅ 成功获取M3U8内容")
            print(f"内容长度: {len(m3u8_content)} 字符")
            
            # 保存M3U8内容
            with open("playlist.m3u8", "w", encoding="utf-8") as f:
                f.write(m3u8_content)
            print(f"💾 M3U8内容已保存到: playlist.m3u8")
            
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
                with open("video_segments.txt", "w", encoding="utf-8") as f:
                    for segment in video_segments:
                        f.write(f"{segment}\n")
                print(f"\n💾 所有视频片段链接已保存到: video_segments.txt")
                
                # 创建完整的结果报告
                result = {
                    'main_m3u8_url': video_url,
                    'm3u8_content': m3u8_content,
                    'video_segments': video_segments,
                    'total_segments': len(video_segments),
                    'domain': parsed.netloc,
                    'path': parsed.path,
                    'query_params': parsed.query
                }
                
                with open("complete_video_analysis.json", "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                print(f"💾 完整分析结果已保存到: complete_video_analysis.json")
                
            else:
                print("❌ 未找到视频片段")
        else:
            print("❌ 获取M3U8内容失败")
    else:
        print("❌ 未找到视频链接")
    
    print(f"\n🎉 视频链接提取完成!")
    if video_url:
        print(f"🎬 主要视频链接: {video_url}")
        print(f"📱 这是一个HLS流媒体链接，可以在支持HLS的播放器中播放")
        print(f"🔗 推荐使用VLC、PotPlayer等播放器打开此链接")


if __name__ == "__main__":
    main()
