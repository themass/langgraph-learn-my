#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接视频链接提取器
专门用于获取视频页面的实际视频流地址
"""

import requests
import json
import re
import time
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Any, Optional


class DirectVideoExtractor:
    """直接视频链接提取器"""
    
    def __init__(self):
        """初始化提取器"""
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """设置请求会话"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })
    
    def extract_video_links(self, url: str) -> Dict[str, Any]:
        """
        提取视频链接
        
        Args:
            url: 视频页面URL
            
        Returns:
            视频链接信息
        """
        print(f"🎬 提取视频链接: {url}")
        print("=" * 60)
        
        result = {
            'url': url,
            'video_links': [],
            'm3u8_links': [],
            'mp4_links': [],
            'stream_links': [],
            'extraction_methods': []
        }
        
        try:
            # 方法1: 直接获取页面内容
            print("📄 方法1: 直接获取页面内容...")
            page_links = self._extract_from_page(url)
            result['video_links'].extend(page_links)
            result['extraction_methods'].append('page_content')
            
            # 方法2: 尝试不同的API端点
            print("🔗 方法2: 尝试API端点...")
            api_links = self._extract_from_apis(url)
            result['video_links'].extend(api_links)
            result['extraction_methods'].append('api_endpoints')
            
            # 方法3: 分析JavaScript文件
            print("📜 方法3: 分析JavaScript文件...")
            js_links = self._extract_from_javascript()
            result['video_links'].extend(js_links)
            result['extraction_methods'].append('javascript_analysis')
            
            # 方法4: 尝试常见的视频API模式
            print("🎯 方法4: 尝试常见视频API模式...")
            pattern_links = self._extract_with_patterns(url)
            result['video_links'].extend(pattern_links)
            result['extraction_methods'].append('pattern_matching')
            
            # 分类链接
            result['m3u8_links'] = [link for link in result['video_links'] if '.m3u8' in link.lower()]
            result['mp4_links'] = [link for link in result['video_links'] if '.mp4' in link.lower()]
            result['stream_links'] = [link for link in result['video_links'] if any(keyword in link.lower() for keyword in ['stream', 'play', 'video'])]
            
            # 去重
            result['video_links'] = list(set(result['video_links']))
            result['m3u8_links'] = list(set(result['m3u8_links']))
            result['mp4_links'] = list(set(result['mp4_links']))
            result['stream_links'] = list(set(result['stream_links']))
            
        except Exception as e:
            print(f"❌ 提取失败: {e}")
            result['error'] = str(e)
        
        return result
    
    def _extract_from_page(self, url: str) -> List[str]:
        """从页面内容中提取视频链接"""
        video_links = []
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            content = response.text
            print(f"  ✅ 获取页面内容成功，大小: {len(content)} 字符")
            
            # 查找视频链接模式
            patterns = [
                r'["\']([^"\']*\.m3u8[^"\']*)["\']',
                r'["\']([^"\']*\.mp4[^"\']*)["\']',
                r'["\']([^"\']*\.ts[^"\']*)["\']',
                r'["\']([^"\']*video[^"\']*)["\']',
                r'["\']([^"\']*play[^"\']*)["\']',
                r'["\']([^"\']*stream[^"\']*)["\']',
                r'["\']([^"\']*media[^"\']*)["\']',
                r'src\s*[:=]\s*["\']([^"\']+)["\']',
                r'url\s*[:=]\s*["\']([^"\']+)["\']',
                r'videoUrl\s*[:=]\s*["\']([^"\']+)["\']',
                r'playUrl\s*[:=]\s*["\']([^"\']+)["\']',
                r'streamUrl\s*[:=]\s*["\']([^"\']+)["\']',
                r'mediaUrl\s*[:=]\s*["\']([^"\']+)["\']',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if self._is_valid_video_url(match):
                        video_links.append(match)
            
            print(f"  ✅ 从页面内容中找到 {len(video_links)} 个视频链接")
            
        except Exception as e:
            print(f"  ❌ 页面内容提取失败: {e}")
        
        return video_links
    
    def _extract_from_apis(self, base_url: str) -> List[str]:
        """从API端点中提取视频链接"""
        video_links = []
        
        # 构建可能的API端点
        video_id = base_url.split('/')[-1]
        api_endpoints = [
            f"{base_url}/data",
            f"{base_url}/info",
            f"{base_url}/details",
            f"{base_url}/api/video/{video_id}",
            f"{base_url}/api/data/{video_id}",
            f"{base_url}/api/info/{video_id}",
            f"{base_url}/api/details/{video_id}",
            f"{base_url}/api/play/{video_id}",
            f"{base_url}/api/stream/{video_id}",
            f"{base_url}/api/media/{video_id}",
            f"{base_url}/api/video/info/{video_id}",
            f"{base_url}/api/video/play/{video_id}",
            f"{base_url}/api/video/stream/{video_id}",
            f"{base_url}/api/video/media/{video_id}",
        ]
        
        for endpoint in api_endpoints:
            try:
                response = self.session.get(endpoint, timeout=10)
                if response.status_code == 200:
                    content = response.text
                    
                    # 在响应中查找视频链接
                    patterns = [
                        r'["\']([^"\']*\.m3u8[^"\']*)["\']',
                        r'["\']([^"\']*\.mp4[^"\']*)["\']',
                        r'["\']([^"\']*\.ts[^"\']*)["\']',
                        r'["\']([^"\']*video[^"\']*)["\']',
                        r'["\']([^"\']*play[^"\']*)["\']',
                        r'["\']([^"\']*stream[^"\']*)["\']',
                        r'["\']([^"\']*media[^"\']*)["\']',
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for match in matches:
                            if self._is_valid_video_url(match):
                                video_links.append(match)
                
            except Exception as e:
                continue
        
        print(f"  ✅ 从API端点中找到 {len(video_links)} 个视频链接")
        return video_links
    
    def _extract_from_javascript(self) -> List[str]:
        """从JavaScript文件中提取视频链接"""
        video_links = []
        
        try:
            # 获取主JavaScript文件
            js_url = "https://mjs.szaction.cc/build1/static/js/main.0b1a4dad.js"
            response = self.session.get(js_url, timeout=30)
            response.raise_for_status()
            
            js_content = response.text
            print(f"  ✅ 获取JavaScript文件成功，大小: {len(js_content)} 字符")
            
            # 查找视频链接模式
            patterns = [
                r'["\']([^"\']*\.m3u8[^"\']*)["\']',
                r'["\']([^"\']*\.mp4[^"\']*)["\']',
                r'["\']([^"\']*\.ts[^"\']*)["\']',
                r'["\']([^"\']*video[^"\']*)["\']',
                r'["\']([^"\']*play[^"\']*)["\']',
                r'["\']([^"\']*stream[^"\']*)["\']',
                r'["\']([^"\']*media[^"\']*)["\']',
                r'src\s*[:=]\s*["\']([^"\']+)["\']',
                r'url\s*[:=]\s*["\']([^"\']+)["\']',
                r'videoUrl\s*[:=]\s*["\']([^"\']+)["\']',
                r'playUrl\s*[:=]\s*["\']([^"\']+)["\']',
                r'streamUrl\s*[:=]\s*["\']([^"\']+)["\']',
                r'mediaUrl\s*[:=]\s*["\']([^"\']+)["\']',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, js_content, re.IGNORECASE)
                for match in matches:
                    if self._is_valid_video_url(match):
                        video_links.append(match)
            
            print(f"  ✅ 从JavaScript文件中找到 {len(video_links)} 个视频链接")
            
        except Exception as e:
            print(f"  ❌ JavaScript文件提取失败: {e}")
        
        return video_links
    
    def _extract_with_patterns(self, base_url: str) -> List[str]:
        """使用常见模式提取视频链接"""
        video_links = []
        
        # 常见的视频链接模式
        video_id = base_url.split('/')[-1]
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
        
        # 测试这些模式
        for pattern in patterns:
            try:
                response = self.session.head(pattern, timeout=5)
                if response.status_code == 200:
                    video_links.append(pattern)
                    print(f"  ✅ 找到有效视频链接: {pattern}")
            except:
                continue
        
        print(f"  ✅ 通过模式匹配找到 {len(video_links)} 个视频链接")
        return video_links
    
    def _is_valid_video_url(self, url: str) -> bool:
        """检查是否为有效的视频URL"""
        if not url or len(url) < 10:
            return False
        
        # 排除明显不是视频的URL
        exclude_patterns = [
            'javascript:', 'data:', 'mailto:', 'tel:', 'ftp:',
            '.css', '.js', '.json', '.xml', '.txt', '.pdf',
            'favicon', 'icon', 'logo', 'banner', 'advertisement',
            'function', 'var ', 'let ', 'const ', 'return',
            'true', 'false', 'null', 'undefined', 'http://',
            'https://', 'www.', '.com', '.org', '.net'
        ]
        
        url_lower = url.lower()
        if any(pattern in url_lower for pattern in exclude_patterns):
            return False
        
        # 检查视频文件扩展名
        video_extensions = ['.mp4', '.webm', '.ogg', '.avi', '.mov', '.flv', '.mkv', '.m3u8', '.ts']
        if any(ext in url_lower for ext in video_extensions):
            return True
        
        # 检查视频相关关键词
        video_keywords = ['video', 'play', 'stream', 'media', 'movie', 'film', 'hls', 'dash']
        if any(keyword in url_lower for keyword in video_keywords):
            return True
        
        return False
    
    def print_video_links(self, result: Dict[str, Any]):
        """打印视频链接"""
        print("\n" + "=" * 60)
        print("🎬 视频链接提取结果")
        print("=" * 60)
        
        if result.get('error'):
            print(f"❌ 提取失败: {result['error']}")
            return
        
        print(f"🌐 目标URL: {result['url']}")
        print(f"📊 提取方法: {', '.join(result['extraction_methods'])}")
        
        # 打印所有视频链接
        if result['video_links']:
            print(f"\n🎬 所有视频链接 ({len(result['video_links'])} 个):")
            for i, link in enumerate(result['video_links'], 1):
                print(f"  {i}. {link}")
        else:
            print(f"\n❌ 未找到视频链接")
        
        # 打印M3U8链接
        if result['m3u8_links']:
            print(f"\n📺 M3U8流媒体链接 ({len(result['m3u8_links'])} 个):")
            for i, link in enumerate(result['m3u8_links'], 1):
                print(f"  {i}. {link}")
        
        # 打印MP4链接
        if result['mp4_links']:
            print(f"\n🎥 MP4视频链接 ({len(result['mp4_links'])} 个):")
            for i, link in enumerate(result['mp4_links'], 1):
                print(f"  {i}. {link}")
        
        # 打印流媒体链接
        if result['stream_links']:
            print(f"\n🌊 流媒体链接 ({len(result['stream_links'])} 个):")
            for i, link in enumerate(result['stream_links'], 1):
                print(f"  {i}. {link}")
        
        # 如果没有找到链接，提供建议
        if not result['video_links']:
            print(f"\n💡 建议:")
            print(f"  1. 该页面可能使用动态加载，需要JavaScript执行")
            print(f"  2. 可能需要特定的请求头或认证")
            print(f"  3. 视频链接可能被加密或混淆")
            print(f"  4. 建议使用浏览器开发者工具查看网络请求")


def main():
    """主函数"""
    print("直接视频链接提取器")
    print("=" * 60)
    
    # 目标URL
    target_url = "https://www.a3m5m.com/s/video/shipin/1044455"
    
    # 创建提取器
    extractor = DirectVideoExtractor()
    
    # 提取视频链接
    result = extractor.extract_video_links(target_url)
    
    # 打印结果
    extractor.print_video_links(result)
    
    # 保存结果
    try:
        timestamp = int(time.time())
        filename = f"direct_video_links_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 结果已保存到: {filename}")
    except Exception as e:
        print(f"\n❌ 保存失败: {e}")


if __name__ == "__main__":
    main()
