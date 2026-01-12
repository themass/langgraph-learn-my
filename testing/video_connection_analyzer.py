#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频连接分析器
分析提取到的视频页面连接信息，找出实际的视频流地址
"""

import json
import re
import requests
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Any, Optional


class VideoConnectionAnalyzer:
    """视频连接分析器"""
    
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
        })
    
    def analyze_connections(self, connections_file: str) -> Dict[str, Any]:
        """
        分析连接信息文件
        
        Args:
            connections_file: 连接信息JSON文件路径
            
        Returns:
            分析结果
        """
        print(f"🔍 分析连接信息文件: {connections_file}")
        print("=" * 60)
        
        try:
            with open(connections_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            return {'error': str(e)}
        
        result = {
            'base_url': data.get('base_url', ''),
            'video_streams': [],
            'api_endpoints': [],
            'cdn_servers': [],
            'player_configs': [],
            'analysis_summary': {}
        }
        
        # 分析视频连接
        video_connections = data.get('video_connections', {})
        result['video_streams'] = self._analyze_video_streams(video_connections)
        
        # 分析API端点
        api_connections = data.get('api_connections', {})
        result['api_endpoints'] = self._analyze_api_endpoints(api_connections)
        
        # 分析CDN服务器
        result['cdn_servers'] = self._analyze_cdn_servers(data)
        
        # 分析播放器配置
        result['player_configs'] = self._analyze_player_configs(video_connections)
        
        # 生成分析摘要
        result['analysis_summary'] = self._generate_summary(result)
        
        return result
    
    def _analyze_video_streams(self, video_connections: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析视频流连接"""
        print("🎬 分析视频流连接...")
        
        streams = []
        
        # 分析视频URL
        video_urls = video_connections.get('video_urls', [])
        for video in video_urls:
            url = video.get('url', '')
            if self._is_valid_video_url(url):
                stream_info = {
                    'url': url,
                    'type': 'video',
                    'format': self._detect_video_format(url),
                    'domain': urlparse(url).netloc if url.startswith('http') else 'relative',
                    'priority': self._calculate_priority(url)
                }
                streams.append(stream_info)
        
        # 分析流媒体URL
        stream_urls = video_connections.get('stream_urls', [])
        for stream in stream_urls:
            url = stream.get('url', '')
            if self._is_valid_stream_url(url):
                stream_info = {
                    'url': url,
                    'type': 'stream',
                    'format': self._detect_stream_format(url),
                    'domain': urlparse(url).netloc if url.startswith('http') else 'relative',
                    'priority': self._calculate_priority(url)
                }
                streams.append(stream_info)
        
        # 按优先级排序
        streams.sort(key=lambda x: x['priority'], reverse=True)
        
        print(f"  ✅ 找到 {len(streams)} 个有效视频流")
        return streams
    
    def _analyze_api_endpoints(self, api_connections: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析API端点"""
        print("🔗 分析API端点...")
        
        endpoints = []
        
        # 分析视频API
        video_apis = api_connections.get('video_apis', [])
        for api in video_apis:
            url = api.get('url', '')
            if self._is_valid_api_url(url):
                endpoint_info = {
                    'url': url,
                    'type': 'video_api',
                    'domain': urlparse(url).netloc,
                    'priority': self._calculate_api_priority(url)
                }
                endpoints.append(endpoint_info)
        
        # 分析数据API
        data_apis = api_connections.get('data_apis', [])
        for api in data_apis:
            url = api.get('url', '')
            if self._is_valid_api_url(url):
                endpoint_info = {
                    'url': url,
                    'type': 'data_api',
                    'domain': urlparse(url).netloc,
                    'priority': self._calculate_api_priority(url)
                }
                endpoints.append(endpoint_info)
        
        # 按优先级排序
        endpoints.sort(key=lambda x: x['priority'], reverse=True)
        
        print(f"  ✅ 找到 {len(endpoints)} 个有效API端点")
        return endpoints
    
    def _analyze_cdn_servers(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析CDN服务器"""
        print("🌐 分析CDN服务器...")
        
        cdn_servers = []
        
        # 从API连接中提取CDN
        api_connections = data.get('api_connections', {})
        cdn_apis = api_connections.get('cdn_apis', [])
        
        for cdn in cdn_apis:
            url = cdn.get('url', '')
            domain = cdn.get('domain', '')
            
            if domain and self._is_valid_cdn_domain(domain):
                cdn_info = {
                    'url': url,
                    'domain': domain,
                    'type': 'cdn',
                    'priority': self._calculate_cdn_priority(domain)
                }
                cdn_servers.append(cdn_info)
        
        # 从外部域名中提取CDN
        video_connections = data.get('video_connections', {})
        external_domains = video_connections.get('external_domains', [])
        
        for domain in external_domains:
            if self._is_valid_cdn_domain(domain):
                cdn_info = {
                    'url': f"https://{domain}/",
                    'domain': domain,
                    'type': 'cdn',
                    'priority': self._calculate_cdn_priority(domain)
                }
                cdn_servers.append(cdn_info)
        
        # 去重并按优先级排序
        seen = set()
        unique_cdns = []
        for cdn in cdn_servers:
            if cdn['domain'] not in seen:
                seen.add(cdn['domain'])
                unique_cdns.append(cdn)
        
        unique_cdns.sort(key=lambda x: x['priority'], reverse=True)
        
        print(f"  ✅ 找到 {len(unique_cdns)} 个CDN服务器")
        return unique_cdns
    
    def _analyze_player_configs(self, video_connections: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析播放器配置"""
        print("🎮 分析播放器配置...")
        
        configs = []
        
        # 从外部域名中识别播放器相关域名
        external_domains = video_connections.get('external_domains', [])
        
        player_domains = [
            'dplayer.diygod.dev',
            'github.com',
            'momentjs.com',
            'reactjs.org'
        ]
        
        for domain in external_domains:
            if any(player in domain.lower() for player in ['dplayer', 'player', 'video', 'stream']):
                config_info = {
                    'domain': domain,
                    'type': 'player_related',
                    'priority': self._calculate_player_priority(domain)
                }
                configs.append(config_info)
        
        # 按优先级排序
        configs.sort(key=lambda x: x['priority'], reverse=True)
        
        print(f"  ✅ 找到 {len(configs)} 个播放器相关配置")
        return configs
    
    def _is_valid_video_url(self, url: str) -> bool:
        """检查是否为有效的视频URL"""
        if not url or len(url) < 10:
            return False
        
        # 检查视频文件扩展名
        video_extensions = ['.mp4', '.webm', '.ogg', '.avi', '.mov', '.flv', '.mkv', '.m3u8', '.ts']
        if any(ext in url.lower() for ext in video_extensions):
            return True
        
        # 检查视频相关关键词
        video_keywords = ['video', 'play', 'stream', 'media', 'movie', 'film']
        if any(keyword in url.lower() for keyword in video_keywords):
            return True
        
        return False
    
    def _is_valid_stream_url(self, url: str) -> bool:
        """检查是否为有效的流媒体URL"""
        if not url or len(url) < 10:
            return False
        
        # 检查流媒体格式
        stream_formats = ['.m3u8', '.ts', 'hls', 'dash', 'stream']
        if any(fmt in url.lower() for fmt in stream_formats):
            return True
        
        return False
    
    def _is_valid_api_url(self, url: str) -> bool:
        """检查是否为有效的API URL"""
        if not url or len(url) < 10:
            return False
        
        # 检查API相关关键词
        api_keywords = ['api', 'ajax', 'json', 'data', 'info', 'details']
        if any(keyword in url.lower() for keyword in api_keywords):
            return True
        
        return False
    
    def _is_valid_cdn_domain(self, domain: str) -> bool:
        """检查是否为有效的CDN域名"""
        if not domain or len(domain) < 5:
            return False
        
        # 检查CDN相关关键词
        cdn_keywords = ['cdn', 'static', 'assets', 'media', 'video', 'stream', 'mjs', 'mjson']
        if any(keyword in domain.lower() for keyword in cdn_keywords):
            return True
        
        return False
    
    def _detect_video_format(self, url: str) -> str:
        """检测视频格式"""
        url_lower = url.lower()
        
        if '.mp4' in url_lower:
            return 'mp4'
        elif '.webm' in url_lower:
            return 'webm'
        elif '.ogg' in url_lower:
            return 'ogg'
        elif '.avi' in url_lower:
            return 'avi'
        elif '.mov' in url_lower:
            return 'mov'
        elif '.flv' in url_lower:
            return 'flv'
        elif '.mkv' in url_lower:
            return 'mkv'
        else:
            return 'unknown'
    
    def _detect_stream_format(self, url: str) -> str:
        """检测流媒体格式"""
        url_lower = url.lower()
        
        if '.m3u8' in url_lower or 'hls' in url_lower:
            return 'hls'
        elif '.ts' in url_lower:
            return 'hls_segment'
        elif 'dash' in url_lower:
            return 'dash'
        else:
            return 'unknown'
    
    def _calculate_priority(self, url: str) -> int:
        """计算URL优先级"""
        priority = 0
        
        # 基于URL长度
        priority += max(0, 100 - len(url))
        
        # 基于域名可信度
        domain = urlparse(url).netloc
        trusted_domains = ['mjs.szaction.cc', 'mjson.szaction.cc', 'cdn.a3m5m.com']
        if domain in trusted_domains:
            priority += 50
        
        # 基于文件扩展名
        if any(ext in url.lower() for ext in ['.mp4', '.m3u8']):
            priority += 30
        elif any(ext in url.lower() for ext in ['.webm', '.ts']):
            priority += 20
        
        return priority
    
    def _calculate_api_priority(self, url: str) -> int:
        """计算API优先级"""
        priority = 0
        
        # 基于URL长度
        priority += max(0, 100 - len(url))
        
        # 基于API类型
        if 'video' in url.lower():
            priority += 40
        elif 'api' in url.lower():
            priority += 30
        elif 'data' in url.lower():
            priority += 20
        
        return priority
    
    def _calculate_cdn_priority(self, domain: str) -> int:
        """计算CDN优先级"""
        priority = 0
        
        # 基于域名长度
        priority += max(0, 50 - len(domain))
        
        # 基于CDN类型
        if 'mjs' in domain.lower():
            priority += 40
        elif 'cdn' in domain.lower():
            priority += 30
        elif 'static' in domain.lower():
            priority += 20
        
        return priority
    
    def _calculate_player_priority(self, domain: str) -> int:
        """计算播放器优先级"""
        priority = 0
        
        # 基于域名长度
        priority += max(0, 50 - len(domain))
        
        # 基于播放器类型
        if 'dplayer' in domain.lower():
            priority += 40
        elif 'player' in domain.lower():
            priority += 30
        elif 'video' in domain.lower():
            priority += 20
        
        return priority
    
    def _generate_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """生成分析摘要"""
        summary = {
            'total_video_streams': len(result['video_streams']),
            'total_api_endpoints': len(result['api_endpoints']),
            'total_cdn_servers': len(result['cdn_servers']),
            'total_player_configs': len(result['player_configs']),
            'top_video_streams': result['video_streams'][:5],
            'top_api_endpoints': result['api_endpoints'][:5],
            'top_cdn_servers': result['cdn_servers'][:5],
            'recommended_connections': []
        }
        
        # 推荐连接
        if result['video_streams']:
            summary['recommended_connections'].append({
                'type': 'video_stream',
                'url': result['video_streams'][0]['url'],
                'reason': '最高优先级的视频流'
            })
        
        if result['api_endpoints']:
            summary['recommended_connections'].append({
                'type': 'api_endpoint',
                'url': result['api_endpoints'][0]['url'],
                'reason': '最高优先级的API端点'
            })
        
        if result['cdn_servers']:
            summary['recommended_connections'].append({
                'type': 'cdn_server',
                'url': result['cdn_servers'][0]['url'],
                'reason': '最高优先级的CDN服务器'
            })
        
        return summary
    
    def save_analysis(self, result: Dict[str, Any], filename: str = None) -> str:
        """保存分析结果"""
        if not filename:
            domain = urlparse(result['base_url']).netloc
            timestamp = int(time.time())
            filename = f"video_analysis_{domain}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 分析结果已保存到: {filename}")
            return filename
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return ""


def main():
    """主函数"""
    print("视频连接分析器")
    print("=" * 60)
    
    # 连接信息文件
    connections_file = "video_connections_www.a3m5m.com_1759163148.json"
    
    # 创建分析器
    analyzer = VideoConnectionAnalyzer()
    
    # 分析连接信息
    result = analyzer.analyze_connections(connections_file)
    
    if 'error' not in result:
        print(f"\n🎉 连接分析完成!")
        print(f"🌐 基础URL: {result['base_url']}")
        
        # 显示分析摘要
        summary = result['analysis_summary']
        print(f"\n📊 分析摘要:")
        print(f"  视频流: {summary['total_video_streams']} 个")
        print(f"  API端点: {summary['total_api_endpoints']} 个")
        print(f"  CDN服务器: {summary['total_cdn_servers']} 个")
        print(f"  播放器配置: {summary['total_player_configs']} 个")
        
        # 显示推荐连接
        print(f"\n🎯 推荐连接:")
        for i, conn in enumerate(summary['recommended_connections'], 1):
            print(f"  {i}. {conn['type']}: {conn['url']}")
            print(f"     原因: {conn['reason']}")
        
        # 显示详细连接列表
        print(f"\n📋 详细连接列表:")
        print("-" * 60)
        
        # 视频流
        if result['video_streams']:
            print(f"\n🎬 视频流 (前10个):")
            for i, stream in enumerate(result['video_streams'][:10], 1):
                print(f"  {i}. {stream['url']}")
                print(f"     类型: {stream['type']}, 格式: {stream['format']}, 优先级: {stream['priority']}")
        
        # API端点
        if result['api_endpoints']:
            print(f"\n🔗 API端点 (前10个):")
            for i, endpoint in enumerate(result['api_endpoints'][:10], 1):
                print(f"  {i}. {endpoint['url']}")
                print(f"     类型: {endpoint['type']}, 优先级: {endpoint['priority']}")
        
        # CDN服务器
        if result['cdn_servers']:
            print(f"\n🌐 CDN服务器 (前10个):")
            for i, cdn in enumerate(result['cdn_servers'][:10], 1):
                print(f"  {i}. {cdn['url']}")
                print(f"     域名: {cdn['domain']}, 优先级: {cdn['priority']}")
        
        # 保存分析结果
        filename = analyzer.save_analysis(result)
        
    else:
        print(f"\n❌ 分析失败: {result['error']}")


if __name__ == "__main__":
    import time
    main()
