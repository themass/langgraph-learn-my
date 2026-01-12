#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度视频页面分析工具
专门分析React应用和动态加载的视频内容
"""

import requests
import json
import re
import time
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Optional, Any


class DeepVideoAnalyzer:
    """深度视频分析器"""
    
    def __init__(self):
        """初始化分析器"""
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
    
    def analyze_react_app(self, base_url: str) -> Dict[str, Any]:
        """
        分析React应用
        
        Args:
            base_url: 基础URL
            
        Returns:
            分析结果
        """
        print(f"🔍 深度分析React应用: {base_url}")
        print("=" * 60)
        
        result = {
            'base_url': base_url,
            'main_js_analysis': {},
            'css_analysis': {},
            'api_analysis': {},
            'video_info': {},
            'success': False
        }
        
        try:
            # 分析主JavaScript文件
            main_js_url = "https://mjs.szaction.cc/build1/static/js/main.0b1a4dad.js"
            print(f"📜 分析主JavaScript文件: {main_js_url}")
            
            js_analysis = self._analyze_js_file(main_js_url)
            result['main_js_analysis'] = js_analysis
            
            # 分析CSS文件
            css_url = "https://mjs.szaction.cc/build1/static/css/main.e5ec3bb5.css"
            print(f"🎨 分析CSS文件: {css_url}")
            
            css_analysis = self._analyze_css_file(css_url)
            result['css_analysis'] = css_analysis
            
            # 分析可能的API端点
            api_analysis = self._analyze_api_endpoints(base_url)
            result['api_analysis'] = api_analysis
            
            # 分析视频相关信息
            video_info = self._extract_video_info_from_js(js_analysis)
            result['video_info'] = video_info
            
            result['success'] = True
            
        except Exception as e:
            print(f"❌ 分析失败: {e}")
            result['error'] = str(e)
        
        return result
    
    def _analyze_js_file(self, js_url: str) -> Dict[str, Any]:
        """分析JavaScript文件"""
        try:
            response = self.session.get(js_url, timeout=30)
            response.raise_for_status()
            
            js_content = response.text
            print(f"  ✅ 获取JS文件成功，大小: {len(js_content)} 字符")
            
            analysis = {
                'url': js_url,
                'size': len(js_content),
                'video_urls': [],
                'api_endpoints': [],
                'video_configs': [],
                'player_configs': [],
                'stream_urls': [],
                'encrypted_content': [],
                'base64_content': []
            }
            
            # 查找视频URL模式
            video_patterns = [
                r'["\']([^"\']*\.(?:mp4|webm|ogg|avi|mov|flv|mkv|m3u8|ts))["\']',
                r'["\']([^"\']*video[^"\']*)["\']',
                r'["\']([^"\']*play[^"\']*)["\']',
                r'["\']([^"\']*stream[^"\']*)["\']',
                r'["\']([^"\']*media[^"\']*)["\']',
                r'src\s*[:=]\s*["\']([^"\']+)["\']',
                r'url\s*[:=]\s*["\']([^"\']+)["\']',
                r'videoUrl\s*[:=]\s*["\']([^"\']+)["\']',
                r'playUrl\s*[:=]\s*["\']([^"\']+)["\']'
            ]
            
            for pattern in video_patterns:
                matches = re.findall(pattern, js_content, re.IGNORECASE)
                for match in matches:
                    if match and len(match) > 10 and not match.startswith('data:'):
                        analysis['video_urls'].append(match)
            
            # 查找API端点
            api_patterns = [
                r'["\']([^"\']*api[^"\']*)["\']',
                r'["\']([^"\']*ajax[^"\']*)["\']',
                r'["\']([^"\']*json[^"\']*)["\']',
                r'["\']([^"\']*data[^"\']*)["\']',
                r'fetch\s*\(\s*["\']([^"\']+)["\']',
                r'axios\.[get|post]\s*\(\s*["\']([^"\']+)["\']'
            ]
            
            for pattern in api_patterns:
                matches = re.findall(pattern, js_content, re.IGNORECASE)
                for match in matches:
                    if match and len(match) > 5:
                        analysis['api_endpoints'].append(match)
            
            # 查找视频配置
            config_patterns = [
                r'videoConfig\s*[:=]\s*({[^}]+})',
                r'playerConfig\s*[:=]\s*({[^}]+})',
                r'videoSettings\s*[:=]\s*({[^}]+})',
                r'playbackConfig\s*[:=]\s*({[^}]+})'
            ]
            
            for pattern in config_patterns:
                matches = re.findall(pattern, js_content, re.IGNORECASE)
                for match in matches:
                    try:
                        config = json.loads(match)
                        analysis['video_configs'].append(config)
                    except:
                        analysis['video_configs'].append(match)
            
            # 查找流媒体URL
            stream_patterns = [
                r'["\']([^"\']*\.m3u8[^"\']*)["\']',
                r'["\']([^"\']*\.ts[^"\']*)["\']',
                r'["\']([^"\']*hls[^"\']*)["\']',
                r'["\']([^"\']*dash[^"\']*)["\']'
            ]
            
            for pattern in stream_patterns:
                matches = re.findall(pattern, js_content, re.IGNORECASE)
                for match in matches:
                    if match:
                        analysis['stream_urls'].append(match)
            
            # 查找加密内容
            encrypted_patterns = [
                r'["\']([A-Za-z0-9+/]{20,}={0,2})["\']',  # Base64
                r'encrypt\s*[:=]\s*["\']([^"\']+)["\']',
                r'decode\s*[:=]\s*["\']([^"\']+)["\']'
            ]
            
            for pattern in encrypted_patterns:
                matches = re.findall(pattern, js_content, re.IGNORECASE)
                for match in matches:
                    if len(match) > 20:  # 过滤太短的匹配
                        analysis['encrypted_content'].append(match)
            
            # 去重
            for key in ['video_urls', 'api_endpoints', 'stream_urls', 'encrypted_content']:
                analysis[key] = list(set(analysis[key]))
            
            print(f"  ✅ 找到 {len(analysis['video_urls'])} 个视频URL")
            print(f"  ✅ 找到 {len(analysis['api_endpoints'])} 个API端点")
            print(f"  ✅ 找到 {len(analysis['video_configs'])} 个视频配置")
            print(f"  ✅ 找到 {len(analysis['stream_urls'])} 个流媒体URL")
            print(f"  ✅ 找到 {len(analysis['encrypted_content'])} 个加密内容")
            
            return analysis
            
        except Exception as e:
            print(f"  ❌ 分析JS文件失败: {e}")
            return {'error': str(e)}
    
    def _analyze_css_file(self, css_url: str) -> Dict[str, Any]:
        """分析CSS文件"""
        try:
            response = self.session.get(css_url, timeout=30)
            response.raise_for_status()
            
            css_content = response.text
            print(f"  ✅ 获取CSS文件成功，大小: {len(css_content)} 字符")
            
            analysis = {
                'url': css_url,
                'size': len(css_content),
                'video_classes': [],
                'player_classes': [],
                'media_queries': []
            }
            
            # 查找视频相关CSS类
            video_class_patterns = [
                r'\.([a-zA-Z_-]*video[a-zA-Z_-]*)',
                r'\.([a-zA-Z_-]*player[a-zA-Z_-]*)',
                r'\.([a-zA-Z_-]*media[a-zA-Z_-]*)',
                r'\.([a-zA-Z_-]*stream[a-zA-Z_-]*)'
            ]
            
            for pattern in video_class_patterns:
                matches = re.findall(pattern, css_content, re.IGNORECASE)
                analysis['video_classes'].extend(matches)
            
            # 查找媒体查询
            media_patterns = [
                r'@media\s+([^{]+)',
                r'@supports\s+([^{]+)'
            ]
            
            for pattern in media_patterns:
                matches = re.findall(pattern, css_content, re.IGNORECASE)
                analysis['media_queries'].extend(matches)
            
            # 去重
            analysis['video_classes'] = list(set(analysis['video_classes']))
            analysis['media_queries'] = list(set(analysis['media_queries']))
            
            print(f"  ✅ 找到 {len(analysis['video_classes'])} 个视频相关CSS类")
            print(f"  ✅ 找到 {len(analysis['media_queries'])} 个媒体查询")
            
            return analysis
            
        except Exception as e:
            print(f"  ❌ 分析CSS文件失败: {e}")
            return {'error': str(e)}
    
    def _analyze_api_endpoints(self, base_url: str) -> Dict[str, Any]:
        """分析API端点"""
        print(f"  🔗 分析API端点...")
        
        analysis = {
            'possible_endpoints': [],
            'video_apis': [],
            'data_apis': []
        }
        
        # 常见的视频API端点模式
        api_patterns = [
            f"{base_url}/api/video/",
            f"{base_url}/api/play/",
            f"{base_url}/api/stream/",
            f"{base_url}/api/media/",
            f"{base_url}/video/",
            f"{base_url}/play/",
            f"{base_url}/stream/",
            f"{base_url}/media/",
            f"{base_url}/data/",
            f"{base_url}/json/"
        ]
        
        for endpoint in api_patterns:
            analysis['possible_endpoints'].append(endpoint)
        
        print(f"  ✅ 生成 {len(analysis['possible_endpoints'])} 个可能的API端点")
        
        return analysis
    
    def _extract_video_info_from_js(self, js_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """从JS分析中提取视频信息"""
        print(f"  🎬 提取视频信息...")
        
        video_info = {
            'direct_video_urls': [],
            'stream_urls': [],
            'api_endpoints': [],
            'encrypted_urls': [],
            'player_configs': []
        }
        
        # 从JS分析结果中提取视频信息
        if 'video_urls' in js_analysis:
            for url in js_analysis['video_urls']:
                if any(ext in url.lower() for ext in ['.mp4', '.webm', '.ogg', '.avi', '.mov']):
                    video_info['direct_video_urls'].append(url)
                elif any(ext in url.lower() for ext in ['.m3u8', '.ts']):
                    video_info['stream_urls'].append(url)
                else:
                    video_info['api_endpoints'].append(url)
        
        if 'stream_urls' in js_analysis:
            video_info['stream_urls'].extend(js_analysis['stream_urls'])
        
        if 'encrypted_content' in js_analysis:
            video_info['encrypted_urls'].extend(js_analysis['encrypted_content'])
        
        if 'video_configs' in js_analysis:
            video_info['player_configs'].extend(js_analysis['video_configs'])
        
        print(f"  ✅ 找到 {len(video_info['direct_video_urls'])} 个直接视频URL")
        print(f"  ✅ 找到 {len(video_info['stream_urls'])} 个流媒体URL")
        print(f"  ✅ 找到 {len(video_info['api_endpoints'])} 个API端点")
        print(f"  ✅ 找到 {len(video_info['encrypted_urls'])} 个加密URL")
        
        return video_info
    
    def save_analysis(self, data: Dict[str, Any], filename: str = None) -> str:
        """保存分析结果"""
        if not filename:
            domain = urlparse(data['base_url']).netloc
            timestamp = int(time.time())
            filename = f"deep_video_analysis_{domain}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 深度分析结果已保存到: {filename}")
            return filename
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return ""


def main():
    """主函数"""
    print("深度视频页面分析工具")
    print("=" * 60)
    
    # 目标URL
    target_url = "https://www.a3m5m.com/s/video/shipin/1044455"
    
    # 创建分析器
    analyzer = DeepVideoAnalyzer()
    
    # 分析React应用
    result = analyzer.analyze_react_app(target_url)
    
    if result['success']:
        print(f"\n🎉 深度分析完成!")
        
        # 显示视频信息
        video_info = result['video_info']
        print(f"\n🎬 视频信息总结:")
        print(f"  直接视频URL: {len(video_info['direct_video_urls'])} 个")
        print(f"  流媒体URL: {len(video_info['stream_urls'])} 个")
        print(f"  API端点: {len(video_info['api_endpoints'])} 个")
        print(f"  加密URL: {len(video_info['encrypted_urls'])} 个")
        
        if video_info['direct_video_urls']:
            print(f"\n📹 直接视频URL:")
            for i, url in enumerate(video_info['direct_video_urls'], 1):
                print(f"  {i}. {url}")
        
        if video_info['stream_urls']:
            print(f"\n📺 流媒体URL:")
            for i, url in enumerate(video_info['stream_urls'], 1):
                print(f"  {i}. {url}")
        
        if video_info['api_endpoints']:
            print(f"\n🔗 API端点:")
            for i, url in enumerate(video_info['api_endpoints'][:10], 1):  # 只显示前10个
                print(f"  {i}. {url}")
        
        if video_info['encrypted_urls']:
            print(f"\n🔐 加密URL (前5个):")
            for i, url in enumerate(video_info['encrypted_urls'][:5], 1):
                print(f"  {i}. {url[:50]}...")
        
        # 显示JS分析结果
        js_analysis = result['main_js_analysis']
        if 'video_urls' in js_analysis and js_analysis['video_urls']:
            print(f"\n📜 JavaScript中的视频URL (前10个):")
            for i, url in enumerate(js_analysis['video_urls'][:10], 1):
                print(f"  {i}. {url}")
        
        # 保存分析结果
        filename = analyzer.save_analysis(result)
        
    else:
        print(f"\n❌ 深度分析失败: {result.get('error', '未知错误')}")


if __name__ == "__main__":
    main()
