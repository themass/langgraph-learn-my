#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JavaScript视频信息提取器
直接从主JavaScript文件中提取视频配置和流地址
"""

import requests
import json
import re
import time
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Any, Optional


class JavaScriptVideoExtractor:
    """JavaScript视频信息提取器"""
    
    def __init__(self):
        """初始化提取器"""
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """设置请求会话"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.a3m5m.com/',
        })
    
    def extract_from_main_js(self, main_js_url: str) -> Dict[str, Any]:
        """
        从主JavaScript文件中提取视频信息
        
        Args:
            main_js_url: 主JavaScript文件URL
            
        Returns:
            提取的视频信息
        """
        print(f"🔍 从主JavaScript文件提取视频信息: {main_js_url}")
        print("=" * 60)
        
        result = {
            'main_js_url': main_js_url,
            'video_configs': [],
            'video_urls': [],
            'api_endpoints': [],
            'player_configs': [],
            'extraction_summary': {}
        }
        
        try:
            # 获取主JavaScript文件
            response = self.session.get(main_js_url, timeout=30)
            response.raise_for_status()
            
            js_content = response.text
            print(f"✅ 成功获取JavaScript文件，大小: {len(js_content)} 字符")
            
            # 提取视频配置
            result['video_configs'] = self._extract_video_configs(js_content)
            
            # 提取视频URL
            result['video_urls'] = self._extract_video_urls(js_content)
            
            # 提取API端点
            result['api_endpoints'] = self._extract_api_endpoints(js_content)
            
            # 提取播放器配置
            result['player_configs'] = self._extract_player_configs(js_content)
            
            # 生成提取摘要
            result['extraction_summary'] = self._generate_extraction_summary(result)
            
        except Exception as e:
            print(f"❌ 提取失败: {e}")
            result['error'] = str(e)
        
        return result
    
    def _extract_video_configs(self, js_content: str) -> List[Dict[str, Any]]:
        """提取视频配置"""
        print("🎬 提取视频配置...")
        
        configs = []
        
        # 查找DPlayer配置
        dplayer_patterns = [
            r'new\s+DPlayer\s*\(\s*\{([^}]+)\}',
            r'DPlayer\s*\(\s*\{([^}]+)\}',
            r'player\s*=\s*new\s+DPlayer\s*\(\s*\{([^}]+)\}',
        ]
        
        for pattern in dplayer_patterns:
            matches = re.findall(pattern, js_content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                config = self._parse_dplayer_config(match)
                if config:
                    configs.append(config)
        
        # 查找HLS配置
        hls_patterns = [
            r'Hls\s*\(\s*\{([^}]+)\}',
            r'new\s+Hls\s*\(\s*\{([^}]+)\}',
            r'hls\s*=\s*new\s+Hls\s*\(\s*\{([^}]+)\}',
        ]
        
        for pattern in hls_patterns:
            matches = re.findall(pattern, js_content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                config = self._parse_hls_config(match)
                if config:
                    configs.append(config)
        
        print(f"  ✅ 找到 {len(configs)} 个视频配置")
        return configs
    
    def _extract_video_urls(self, js_content: str) -> List[Dict[str, Any]]:
        """提取视频URL"""
        print("🔗 提取视频URL...")
        
        video_urls = []
        
        # 查找各种视频URL模式
        patterns = [
            # 直接URL
            r'["\']([^"\']*\.(?:mp4|webm|ogg|avi|mov|flv|mkv|m3u8|ts))["\']',
            # 配置对象中的URL
            r'url\s*:\s*["\']([^"\']+)["\']',
            r'src\s*:\s*["\']([^"\']+)["\']',
            r'video\s*:\s*\{[^}]*url\s*:\s*["\']([^"\']+)["\']',
            r'video\s*:\s*\{[^}]*src\s*:\s*["\']([^"\']+)["\']',
            # 播放器配置中的URL
            r'video\s*:\s*["\']([^"\']+)["\']',
            r'play\s*:\s*["\']([^"\']+)["\']',
            r'stream\s*:\s*["\']([^"\']+)["\']',
            r'media\s*:\s*["\']([^"\']+)["\']',
            # 变量赋值
            r'videoUrl\s*=\s*["\']([^"\']+)["\']',
            r'playUrl\s*=\s*["\']([^"\']+)["\']',
            r'streamUrl\s*=\s*["\']([^"\']+)["\']',
            r'mediaUrl\s*=\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            for match in matches:
                if self._is_valid_video_url(match):
                    video_urls.append({
                        'url': match,
                        'type': self._detect_video_type(match),
                        'pattern': pattern
                    })
        
        # 去重
        unique_urls = []
        seen = set()
        for video in video_urls:
            if video['url'] not in seen:
                seen.add(video['url'])
                unique_urls.append(video)
        
        print(f"  ✅ 找到 {len(unique_urls)} 个唯一视频URL")
        return unique_urls
    
    def _extract_api_endpoints(self, js_content: str) -> List[Dict[str, Any]]:
        """提取API端点"""
        print("🔗 提取API端点...")
        
        endpoints = []
        
        # 查找API端点模式
        patterns = [
            r'["\']([^"\']*api[^"\']*)["\']',
            r'["\']([^"\']*ajax[^"\']*)["\']',
            r'["\']([^"\']*json[^"\']*)["\']',
            r'["\']([^"\']*data[^"\']*)["\']',
            r'fetch\s*\(\s*["\']([^"\']+)["\']',
            r'axios\.[get|post]\s*\(\s*["\']([^"\']+)["\']',
            r'XMLHttpRequest.*open\s*\(\s*["\'][^"\']*["\']\s*,\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            for match in matches:
                if self._is_valid_api_url(match):
                    endpoints.append({
                        'url': match,
                        'type': self._detect_api_type(match)
                    })
        
        # 去重
        unique_endpoints = []
        seen = set()
        for endpoint in endpoints:
            if endpoint['url'] not in seen:
                seen.add(endpoint['url'])
                unique_endpoints.append(endpoint)
        
        print(f"  ✅ 找到 {len(unique_endpoints)} 个唯一API端点")
        return unique_endpoints
    
    def _extract_player_configs(self, js_content: str) -> List[Dict[str, Any]]:
        """提取播放器配置"""
        print("🎮 提取播放器配置...")
        
        configs = []
        
        # 查找播放器配置
        patterns = [
            r'player\s*=\s*\{([^}]+)\}',
            r'config\s*=\s*\{([^}]+)\}',
            r'options\s*=\s*\{([^}]+)\}',
            r'settings\s*=\s*\{([^}]+)\}',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, js_content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                config = self._parse_player_config(match)
                if config:
                    configs.append(config)
        
        print(f"  ✅ 找到 {len(configs)} 个播放器配置")
        return configs
    
    def _parse_dplayer_config(self, config_text: str) -> Optional[Dict[str, Any]]:
        """解析DPlayer配置"""
        try:
            config = {}
            
            # 提取常见配置项
            patterns = {
                'video': r'video\s*:\s*["\']([^"\']+)["\']',
                'url': r'url\s*:\s*["\']([^"\']+)["\']',
                'src': r'src\s*:\s*["\']([^"\']+)["\']',
                'type': r'type\s*:\s*["\']([^"\']+)["\']',
                'autoplay': r'autoplay\s*:\s*(true|false)',
                'loop': r'loop\s*:\s*(true|false)',
                'volume': r'volume\s*:\s*([0-9.]+)',
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, config_text, re.IGNORECASE)
                if match:
                    config[key] = match.group(1)
            
            return config if config else None
            
        except Exception:
            return None
    
    def _parse_hls_config(self, config_text: str) -> Optional[Dict[str, Any]]:
        """解析HLS配置"""
        try:
            config = {}
            
            # 提取HLS配置项
            patterns = {
                'url': r'url\s*:\s*["\']([^"\']+)["\']',
                'src': r'src\s*:\s*["\']([^"\']+)["\']',
                'enableWorker': r'enableWorker\s*:\s*(true|false)',
                'lowLatencyMode': r'lowLatencyMode\s*:\s*(true|false)',
                'backBufferLength': r'backBufferLength\s*:\s*([0-9.]+)',
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, config_text, re.IGNORECASE)
                if match:
                    config[key] = match.group(1)
            
            return config if config else None
            
        except Exception:
            return None
    
    def _parse_player_config(self, config_text: str) -> Optional[Dict[str, Any]]:
        """解析播放器配置"""
        try:
            config = {}
            
            # 提取配置项
            patterns = {
                'autoplay': r'autoplay\s*:\s*(true|false)',
                'loop': r'loop\s*:\s*(true|false)',
                'volume': r'volume\s*:\s*([0-9.]+)',
                'width': r'width\s*:\s*([0-9]+)',
                'height': r'height\s*:\s*([0-9]+)',
                'controls': r'controls\s*:\s*(true|false)',
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, config_text, re.IGNORECASE)
                if match:
                    config[key] = match.group(1)
            
            return config if config else None
            
        except Exception:
            return None
    
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
            'true', 'false', 'null', 'undefined'
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
    
    def _is_valid_api_url(self, url: str) -> bool:
        """检查是否为有效的API URL"""
        if not url or len(url) < 10:
            return False
        
        # 排除明显不是API的URL
        exclude_patterns = [
            'javascript:', 'data:', 'mailto:', 'tel:', 'ftp:',
            '.css', '.js', '.json', '.xml', '.txt', '.pdf',
            'favicon', 'icon', 'logo', 'banner', 'advertisement',
            'function', 'var ', 'let ', 'const ', 'return',
            'true', 'false', 'null', 'undefined'
        ]
        
        url_lower = url.lower()
        if any(pattern in url_lower for pattern in exclude_patterns):
            return False
        
        # 检查API相关关键词
        api_keywords = ['api', 'ajax', 'json', 'data', 'info', 'details']
        if any(keyword in url_lower for keyword in api_keywords):
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
    
    def _detect_api_type(self, url: str) -> str:
        """检测API类型"""
        url_lower = url.lower()
        
        if 'video' in url_lower:
            return 'video_api'
        elif 'data' in url_lower:
            return 'data_api'
        elif 'info' in url_lower:
            return 'info_api'
        else:
            return 'general_api'
    
    def _generate_extraction_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """生成提取摘要"""
        summary = {
            'total_video_configs': len(result['video_configs']),
            'total_video_urls': len(result['video_urls']),
            'total_api_endpoints': len(result['api_endpoints']),
            'total_player_configs': len(result['player_configs']),
            'top_video_urls': result['video_urls'][:5],
            'top_api_endpoints': result['api_endpoints'][:5],
            'recommendations': []
        }
        
        # 生成推荐
        if result['video_urls']:
            summary['recommendations'].append({
                'type': 'video_url',
                'url': result['video_urls'][0]['url'],
                'reason': '最高优先级的视频URL'
            })
        
        if result['api_endpoints']:
            summary['recommendations'].append({
                'type': 'api_endpoint',
                'url': result['api_endpoints'][0]['url'],
                'reason': '最高优先级的API端点'
            })
        
        return summary
    
    def save_extraction_results(self, result: Dict[str, Any], filename: str = None) -> str:
        """保存提取结果"""
        if not filename:
            domain = urlparse(result['main_js_url']).netloc
            timestamp = int(time.time())
            filename = f"javascript_video_extraction_{domain}_{timestamp}.json"
        
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
    print("JavaScript视频信息提取器")
    print("=" * 60)
    
    # 主JavaScript文件URL
    main_js_url = "https://mjs.szaction.cc/build1/static/js/main.0b1a4dad.js"
    
    # 创建提取器
    extractor = JavaScriptVideoExtractor()
    
    # 提取视频信息
    result = extractor.extract_from_main_js(main_js_url)
    
    if 'error' not in result:
        print(f"\n🎉 JavaScript视频信息提取完成!")
        print(f"🌐 主JS文件: {result['main_js_url']}")
        
        # 显示提取摘要
        summary = result['extraction_summary']
        print(f"\n📊 提取摘要:")
        print(f"  视频配置: {summary['total_video_configs']} 个")
        print(f"  视频URL: {summary['total_video_urls']} 个")
        print(f"  API端点: {summary['total_api_endpoints']} 个")
        print(f"  播放器配置: {summary['total_player_configs']} 个")
        
        # 显示视频URL
        if result['video_urls']:
            print(f"\n🎬 视频URL (前10个):")
            for i, video in enumerate(result['video_urls'][:10], 1):
                print(f"  {i}. {video['url']}")
                print(f"     类型: {video['type']}")
        
        # 显示API端点
        if result['api_endpoints']:
            print(f"\n🔗 API端点 (前10个):")
            for i, endpoint in enumerate(result['api_endpoints'][:10], 1):
                print(f"  {i}. {endpoint['url']}")
                print(f"     类型: {endpoint['type']}")
        
        # 显示视频配置
        if result['video_configs']:
            print(f"\n⚙️ 视频配置:")
            for i, config in enumerate(result['video_configs'], 1):
                print(f"  {i}. {config}")
        
        # 显示推荐
        if summary['recommendations']:
            print(f"\n🎯 推荐:")
            for rec in summary['recommendations']:
                print(f"  - {rec['type']}: {rec['url']}")
                print(f"    原因: {rec['reason']}")
        
        # 保存结果
        filename = extractor.save_extraction_results(result)
        
    else:
        print(f"\n❌ 提取失败: {result['error']}")


if __name__ == "__main__":
    main()
