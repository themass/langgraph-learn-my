#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终视频信息提取器
从测试成功的API端点中提取实际的视频流地址和播放信息
"""

import requests
import json
import re
import time
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Any, Optional


class FinalVideoExtractor:
    """最终视频信息提取器"""
    
    def __init__(self):
        """初始化提取器"""
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """设置请求会话"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.a3m5m.com/',
        })
    
    def extract_video_info(self, base_url: str) -> Dict[str, Any]:
        """
        提取视频信息
        
        Args:
            base_url: 视频页面基础URL
            
        Returns:
            视频信息
        """
        print(f"🎬 提取视频信息: {base_url}")
        print("=" * 60)
        
        result = {
            'base_url': base_url,
            'video_id': base_url.split('/')[-1],
            'video_streams': [],
            'video_info': {},
            'player_config': {},
            'api_responses': {},
            'extraction_summary': {}
        }
        
        # 提取视频ID
        video_id = result['video_id']
        print(f"📹 视频ID: {video_id}")
        
        # 测试多个API端点
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
        ]
        
        # 测试每个端点
        for i, endpoint in enumerate(api_endpoints, 1):
            print(f"\n🔗 测试端点 {i}: {endpoint}")
            
            try:
                response = self.session.get(endpoint, timeout=10)
                if response.status_code == 200:
                    result['api_responses'][endpoint] = response.text
                    print(f"  ✅ 成功获取响应")
                    
                    # 尝试从响应中提取视频信息
                    video_info = self._extract_video_from_response(response.text, endpoint)
                    if video_info:
                        result['video_streams'].extend(video_info)
                        print(f"  🎬 提取到 {len(video_info)} 个视频流")
                else:
                    print(f"  ❌ 失败: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ 错误: {e}")
        
        # 分析提取到的视频流
        result['video_info'] = self._analyze_video_streams(result['video_streams'])
        
        # 生成提取摘要
        result['extraction_summary'] = self._generate_extraction_summary(result)
        
        return result
    
    def _extract_video_from_response(self, response_text: str, endpoint: str) -> List[Dict[str, Any]]:
        """从响应中提取视频信息"""
        video_streams = []
        
        # 检查是否为HTML页面
        if response_text.startswith('<!doctype html>') or response_text.startswith('<html'):
            print(f"  📄 检测到HTML页面，尝试提取JavaScript中的视频信息")
            
            # 从HTML中提取JavaScript代码
            js_pattern = r'<script[^>]*>(.*?)</script>'
            js_matches = re.findall(js_pattern, response_text, re.DOTALL | re.IGNORECASE)
            
            for js_code in js_matches:
                # 在JavaScript中查找视频URL
                video_urls = self._extract_video_urls_from_js(js_code)
                for url in video_urls:
                    video_streams.append({
                        'url': url,
                        'source': 'javascript',
                        'endpoint': endpoint,
                        'type': self._detect_video_type(url)
                    })
        
        # 检查是否为JSON响应
        elif response_text.strip().startswith('{') or response_text.strip().startswith('['):
            print(f"  📊 检测到JSON响应，尝试解析")
            try:
                json_data = json.loads(response_text)
                video_urls = self._extract_video_urls_from_json(json_data)
                for url in video_urls:
                    video_streams.append({
                        'url': url,
                        'source': 'json',
                        'endpoint': endpoint,
                        'type': self._detect_video_type(url)
                    })
            except json.JSONDecodeError:
                print(f"  ❌ JSON解析失败")
        
        # 在纯文本中查找视频URL
        else:
            print(f"  📝 检测到文本响应，尝试提取视频URL")
            video_urls = self._extract_video_urls_from_text(response_text)
            for url in video_urls:
                video_streams.append({
                    'url': url,
                    'source': 'text',
                    'endpoint': endpoint,
                    'type': self._detect_video_type(url)
                })
        
        return video_streams
    
    def _extract_video_urls_from_js(self, js_code: str) -> List[str]:
        """从JavaScript代码中提取视频URL"""
        video_urls = []
        
        # 查找各种视频URL模式
        patterns = [
            r'["\']([^"\']*\.(?:mp4|webm|ogg|avi|mov|flv|mkv|m3u8|ts))["\']',
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
            matches = re.findall(pattern, js_code, re.IGNORECASE)
            for match in matches:
                if self._is_valid_video_url(match):
                    video_urls.append(match)
        
        return list(set(video_urls))  # 去重
    
    def _extract_video_urls_from_json(self, json_data: Any) -> List[str]:
        """从JSON数据中提取视频URL"""
        video_urls = []
        
        def search_json(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, str) and self._is_valid_video_url(value):
                        video_urls.append(value)
                    elif isinstance(value, (dict, list)):
                        search_json(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    if isinstance(item, str) and self._is_valid_video_url(item):
                        video_urls.append(item)
                    elif isinstance(item, (dict, list)):
                        search_json(item, f"{path}[{i}]")
        
        search_json(json_data)
        return list(set(video_urls))  # 去重
    
    def _extract_video_urls_from_text(self, text: str) -> List[str]:
        """从文本中提取视频URL"""
        video_urls = []
        
        # 查找HTTP/HTTPS URL
        url_pattern = r'https?://[^\s<>"\'{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        
        for url in urls:
            if self._is_valid_video_url(url):
                video_urls.append(url)
        
        return list(set(video_urls))  # 去重
    
    def _is_valid_video_url(self, url: str) -> bool:
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
        
        # 检查视频相关关键词
        video_keywords = ['video', 'play', 'stream', 'media', 'movie', 'film', 'hls', 'dash']
        if any(keyword in url_lower for keyword in video_keywords):
            return True
        
        return False
    
    def _detect_video_type(self, url: str) -> str:
        """检测视频类型"""
        url_lower = url.lower()
        
        if '.m3u8' in url_lower or 'hls' in url_lower:
            return 'hls'
        elif '.ts' in url_lower:
            return 'hls_segment'
        elif '.mp4' in url_lower:
            return 'mp4'
        elif '.webm' in url_lower:
            return 'webm'
        elif 'dash' in url_lower:
            return 'dash'
        else:
            return 'unknown'
    
    def _analyze_video_streams(self, video_streams: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析视频流"""
        if not video_streams:
            return {}
        
        analysis = {
            'total_streams': len(video_streams),
            'stream_types': {},
            'sources': {},
            'endpoints': {},
            'unique_urls': []
        }
        
        # 统计流类型
        for stream in video_streams:
            stream_type = stream['type']
            analysis['stream_types'][stream_type] = analysis['stream_types'].get(stream_type, 0) + 1
        
        # 统计来源
        for stream in video_streams:
            source = stream['source']
            analysis['sources'][source] = analysis['sources'].get(source, 0) + 1
        
        # 统计端点
        for stream in video_streams:
            endpoint = stream['endpoint']
            analysis['endpoints'][endpoint] = analysis['endpoints'].get(endpoint, 0) + 1
        
        # 获取唯一URL
        unique_urls = list(set(stream['url'] for stream in video_streams))
        analysis['unique_urls'] = unique_urls
        
        return analysis
    
    def _generate_extraction_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """生成提取摘要"""
        summary = {
            'total_streams': len(result['video_streams']),
            'unique_streams': len(result['video_info'].get('unique_urls', [])),
            'successful_endpoints': len(result['api_responses']),
            'top_streams': result['video_streams'][:5],
            'recommendations': []
        }
        
        # 生成推荐
        if result['video_streams']:
            summary['recommendations'].append({
                'type': 'video_stream',
                'url': result['video_streams'][0]['url'],
                'reason': '最高优先级的视频流'
            })
        
        return summary
    
    def save_extraction_results(self, result: Dict[str, Any], filename: str = None) -> str:
        """保存提取结果"""
        if not filename:
            domain = urlparse(result['base_url']).netloc
            timestamp = int(time.time())
            filename = f"final_video_extraction_{domain}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 提取结果已保存到: {filename}")
            return filename
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return ""


def main():
    """主函数"""
    print("最终视频信息提取器")
    print("=" * 60)
    
    # 目标URL
    base_url = "https://www.a3m5m.com/s/video/shipin/1044455"
    
    # 创建提取器
    extractor = FinalVideoExtractor()
    
    # 提取视频信息
    result = extractor.extract_video_info(base_url)
    
    print(f"\n🎉 视频信息提取完成!")
    print(f"🌐 基础URL: {result['base_url']}")
    print(f"📹 视频ID: {result['video_id']}")
    
    # 显示提取摘要
    summary = result['extraction_summary']
    print(f"\n📊 提取摘要:")
    print(f"  总视频流: {summary['total_streams']}")
    print(f"  唯一视频流: {summary['unique_streams']}")
    print(f"  成功端点: {summary['successful_endpoints']}")
    
    # 显示视频信息分析
    video_info = result['video_info']
    if video_info:
        print(f"\n🎬 视频信息分析:")
        print(f"  流类型: {video_info['stream_types']}")
        print(f"  来源: {video_info['sources']}")
        print(f"  端点: {video_info['endpoints']}")
        
        # 显示唯一URL
        if video_info['unique_urls']:
            print(f"\n🔗 唯一视频URL:")
            for i, url in enumerate(video_info['unique_urls'], 1):
                print(f"  {i}. {url}")
    
    # 显示推荐
    if summary['recommendations']:
        print(f"\n🎯 推荐:")
        for rec in summary['recommendations']:
            print(f"  - {rec['type']}: {rec['url']}")
            print(f"    原因: {rec['reason']}")
    
    # 保存结果
    filename = extractor.save_extraction_results(result)
    
    # 显示完整的视频流列表
    if result['video_streams']:
        print(f"\n📋 完整视频流列表:")
        print("-" * 60)
        for i, stream in enumerate(result['video_streams'], 1):
            print(f"  {i}. {stream['url']}")
            print(f"     类型: {stream['type']}, 来源: {stream['source']}, 端点: {stream['endpoint']}")


if __name__ == "__main__":
    main()
