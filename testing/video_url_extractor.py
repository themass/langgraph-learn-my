#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频URL提取工具
专门用于提取视频播放页面的完整连接信息
"""

import requests
import json
import re
import time
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Optional, Any


class VideoURLExtractor:
    """视频URL提取器"""
    
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
    
    def extract_video_connections(self, url: str) -> Dict[str, Any]:
        """
        提取视频页面的完整连接信息
        
        Args:
            url: 视频页面URL
            
        Returns:
            包含所有连接信息的字典
        """
        print(f"🔍 提取视频页面连接信息: {url}")
        print("=" * 60)
        
        result = {
            'base_url': url,
            'page_connections': {},
            'video_connections': {},
            'api_connections': {},
            'resource_connections': {},
            'success': False
        }
        
        try:
            # 获取主页面
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            print(f"✅ 主页面获取成功")
            print(f"📊 状态码: {response.status_code}")
            print(f"📏 内容长度: {len(response.content)} 字节")
            
            # 分析主页面连接
            page_connections = self._analyze_page_connections(response.text, url)
            result['page_connections'] = page_connections
            
            # 获取主JavaScript文件
            main_js_url = "https://mjs.szaction.cc/build1/static/js/main.0b1a4dad.js"
            print(f"\n📜 分析主JavaScript文件: {main_js_url}")
            
            js_connections = self._analyze_js_connections(main_js_url)
            result['video_connections'] = js_connections
            
            # 获取CSS文件
            css_url = "https://mjs.szaction.cc/build1/static/css/main.e5ec3bb5.css"
            print(f"\n🎨 分析CSS文件: {css_url}")
            
            css_connections = self._analyze_css_connections(css_url)
            result['resource_connections'] = css_connections
            
            # 分析可能的API连接
            api_connections = self._analyze_api_connections(url)
            result['api_connections'] = api_connections
            
            result['success'] = True
            
        except Exception as e:
            print(f"❌ 提取失败: {e}")
            result['error'] = str(e)
        
        return result
    
    def _analyze_page_connections(self, html_content: str, base_url: str) -> Dict[str, Any]:
        """分析页面连接"""
        print("🔗 分析页面连接...")
        
        connections = {
            'scripts': [],
            'stylesheets': [],
            'images': [],
            'links': [],
            'iframes': []
        }
        
        # 提取脚本连接
        script_pattern = r'<script[^>]*src=["\']([^"\']+)["\'][^>]*>'
        scripts = re.findall(script_pattern, html_content, re.IGNORECASE)
        for script in scripts:
            full_url = urljoin(base_url, script)
            connections['scripts'].append({
                'url': full_url,
                'type': 'script',
                'domain': urlparse(full_url).netloc
            })
        
        # 提取样式表连接
        link_pattern = r'<link[^>]*href=["\']([^"\']+)["\'][^>]*rel=["\']stylesheet["\'][^>]*>'
        stylesheets = re.findall(link_pattern, html_content, re.IGNORECASE)
        for stylesheet in stylesheets:
            full_url = urljoin(base_url, stylesheet)
            connections['stylesheets'].append({
                'url': full_url,
                'type': 'stylesheet',
                'domain': urlparse(full_url).netloc
            })
        
        # 提取图片连接
        img_pattern = r'<img[^>]*src=["\']([^"\']+)["\'][^>]*>'
        images = re.findall(img_pattern, html_content, re.IGNORECASE)
        for img in images:
            full_url = urljoin(base_url, img)
            connections['images'].append({
                'url': full_url,
                'type': 'image',
                'domain': urlparse(full_url).netloc
            })
        
        # 提取链接
        a_pattern = r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>'
        links = re.findall(a_pattern, html_content, re.IGNORECASE)
        for link in links:
            full_url = urljoin(base_url, link)
            connections['links'].append({
                'url': full_url,
                'type': 'link',
                'domain': urlparse(full_url).netloc
            })
        
        # 提取iframe连接
        iframe_pattern = r'<iframe[^>]*src=["\']([^"\']+)["\'][^>]*>'
        iframes = re.findall(iframe_pattern, html_content, re.IGNORECASE)
        for iframe in iframes:
            full_url = urljoin(base_url, iframe)
            connections['iframes'].append({
                'url': full_url,
                'type': 'iframe',
                'domain': urlparse(full_url).netloc
            })
        
        print(f"  ✅ 找到 {len(connections['scripts'])} 个脚本")
        print(f"  ✅ 找到 {len(connections['stylesheets'])} 个样式表")
        print(f"  ✅ 找到 {len(connections['images'])} 个图片")
        print(f"  ✅ 找到 {len(connections['links'])} 个链接")
        print(f"  ✅ 找到 {len(connections['iframes'])} 个iframe")
        
        return connections
    
    def _analyze_js_connections(self, js_url: str) -> Dict[str, Any]:
        """分析JavaScript文件中的连接"""
        try:
            response = self.session.get(js_url, timeout=30)
            response.raise_for_status()
            
            js_content = response.text
            print(f"  ✅ 获取JS文件成功，大小: {len(js_content)} 字符")
            
            connections = {
                'video_urls': [],
                'api_endpoints': [],
                'stream_urls': [],
                'player_configs': [],
                'external_domains': []
            }
            
            # 提取视频URL
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
                        connections['video_urls'].append({
                            'url': match,
                            'type': 'video',
                            'domain': urlparse(match).netloc if match.startswith('http') else 'relative'
                        })
            
            # 提取API端点
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
                        connections['api_endpoints'].append({
                            'url': match,
                            'type': 'api',
                            'domain': urlparse(match).netloc if match.startswith('http') else 'relative'
                        })
            
            # 提取流媒体URL
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
                        connections['stream_urls'].append({
                            'url': match,
                            'type': 'stream',
                            'domain': urlparse(match).netloc if match.startswith('http') else 'relative'
                        })
            
            # 提取外部域名
            domain_pattern = r'https?://([^/"\']+)'
            domains = re.findall(domain_pattern, js_content)
            for domain in domains:
                if domain not in connections['external_domains']:
                    connections['external_domains'].append(domain)
            
            # 去重
            for key in ['video_urls', 'api_endpoints', 'stream_urls']:
                seen = set()
                unique_items = []
                for item in connections[key]:
                    url = item['url']
                    if url not in seen:
                        seen.add(url)
                        unique_items.append(item)
                connections[key] = unique_items
            
            print(f"  ✅ 找到 {len(connections['video_urls'])} 个视频URL")
            print(f"  ✅ 找到 {len(connections['api_endpoints'])} 个API端点")
            print(f"  ✅ 找到 {len(connections['stream_urls'])} 个流媒体URL")
            print(f"  ✅ 找到 {len(connections['external_domains'])} 个外部域名")
            
            return connections
            
        except Exception as e:
            print(f"  ❌ 分析JS文件失败: {e}")
            return {'error': str(e)}
    
    def _analyze_css_connections(self, css_url: str) -> Dict[str, Any]:
        """分析CSS文件中的连接"""
        try:
            response = self.session.get(css_url, timeout=30)
            response.raise_for_status()
            
            css_content = response.text
            print(f"  ✅ 获取CSS文件成功，大小: {len(css_content)} 字符")
            
            connections = {
                'font_urls': [],
                'image_urls': [],
                'external_domains': []
            }
            
            # 提取字体URL
            font_patterns = [
                r'url\(["\']?([^"\']*\.(?:woff|woff2|ttf|eot|otf))["\']?\)',
                r'src\s*:\s*url\(["\']?([^"\']+)["\']?\)'
            ]
            
            for pattern in font_patterns:
                matches = re.findall(pattern, css_content, re.IGNORECASE)
                for match in matches:
                    connections['font_urls'].append({
                        'url': match,
                        'type': 'font',
                        'domain': urlparse(match).netloc if match.startswith('http') else 'relative'
                    })
            
            # 提取图片URL
            img_patterns = [
                r'url\(["\']?([^"\']*\.(?:png|jpg|jpeg|gif|svg|webp))["\']?\)',
                r'background-image\s*:\s*url\(["\']?([^"\']+)["\']?\)'
            ]
            
            for pattern in img_patterns:
                matches = re.findall(pattern, css_content, re.IGNORECASE)
                for match in matches:
                    connections['image_urls'].append({
                        'url': match,
                        'type': 'image',
                        'domain': urlparse(match).netloc if match.startswith('http') else 'relative'
                    })
            
            # 提取外部域名
            domain_pattern = r'https?://([^/"\']+)'
            domains = re.findall(domain_pattern, css_content)
            for domain in domains:
                if domain not in connections['external_domains']:
                    connections['external_domains'].append(domain)
            
            print(f"  ✅ 找到 {len(connections['font_urls'])} 个字体URL")
            print(f"  ✅ 找到 {len(connections['image_urls'])} 个图片URL")
            print(f"  ✅ 找到 {len(connections['external_domains'])} 个外部域名")
            
            return connections
            
        except Exception as e:
            print(f"  ❌ 分析CSS文件失败: {e}")
            return {'error': str(e)}
    
    def _analyze_api_connections(self, base_url: str) -> Dict[str, Any]:
        """分析可能的API连接"""
        print("🔗 分析API连接...")
        
        connections = {
            'video_apis': [],
            'data_apis': [],
            'user_apis': [],
            'cdn_apis': []
        }
        
        # 常见的视频API端点
        video_api_patterns = [
            f"{base_url}/api/video/",
            f"{base_url}/api/play/",
            f"{base_url}/api/stream/",
            f"{base_url}/api/media/",
            f"{base_url}/video/",
            f"{base_url}/play/",
            f"{base_url}/stream/",
            f"{base_url}/media/",
            f"{base_url}/api/video/info/",
            f"{base_url}/api/video/play/",
            f"{base_url}/api/video/stream/"
        ]
        
        for api in video_api_patterns:
            connections['video_apis'].append({
                'url': api,
                'type': 'video_api',
                'domain': urlparse(api).netloc
            })
        
        # 数据API端点
        data_api_patterns = [
            f"{base_url}/api/data/",
            f"{base_url}/api/info/",
            f"{base_url}/api/details/",
            f"{base_url}/data/",
            f"{base_url}/info/",
            f"{base_url}/details/"
        ]
        
        for api in data_api_patterns:
            connections['data_apis'].append({
                'url': api,
                'type': 'data_api',
                'domain': urlparse(api).netloc
            })
        
        # CDN API端点
        cdn_domains = [
            'mjs.szaction.cc',
            'cdn.a3m5m.com',
            'static.a3m5m.com',
            'assets.a3m5m.com'
        ]
        
        for domain in cdn_domains:
            connections['cdn_apis'].append({
                'url': f"https://{domain}/",
                'type': 'cdn',
                'domain': domain
            })
        
        print(f"  ✅ 生成 {len(connections['video_apis'])} 个视频API端点")
        print(f"  ✅ 生成 {len(connections['data_apis'])} 个数据API端点")
        print(f"  ✅ 生成 {len(connections['cdn_apis'])} 个CDN端点")
        
        return connections
    
    def save_connections(self, data: Dict[str, Any], filename: str = None) -> str:
        """保存连接信息"""
        if not filename:
            domain = urlparse(data['base_url']).netloc
            timestamp = int(time.time())
            filename = f"video_connections_{domain}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 连接信息已保存到: {filename}")
            return filename
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return ""


def main():
    """主函数"""
    print("视频URL提取工具")
    print("=" * 60)
    
    # 目标URL
    target_url = "https://www.a3m5m.com/s/video/shipin/1044455"
    
    # 创建提取器
    extractor = VideoURLExtractor()
    
    # 提取连接信息
    result = extractor.extract_video_connections(target_url)
    
    if result['success']:
        print(f"\n🎉 连接信息提取完成!")
        print(f"🌐 基础URL: {result['base_url']}")
        
        # 显示页面连接
        page_conn = result['page_connections']
        print(f"\n📄 页面连接:")
        print(f"  脚本: {len(page_conn['scripts'])} 个")
        print(f"  样式表: {len(page_conn['stylesheets'])} 个")
        print(f"  图片: {len(page_conn['images'])} 个")
        print(f"  链接: {len(page_conn['links'])} 个")
        print(f"  iframe: {len(page_conn['iframes'])} 个")
        
        # 显示视频连接
        video_conn = result['video_connections']
        print(f"\n🎬 视频连接:")
        print(f"  视频URL: {len(video_conn['video_urls'])} 个")
        print(f"  API端点: {len(video_conn['api_endpoints'])} 个")
        print(f"  流媒体URL: {len(video_conn['stream_urls'])} 个")
        print(f"  外部域名: {len(video_conn['external_domains'])} 个")
        
        # 显示资源连接
        resource_conn = result['resource_connections']
        print(f"\n🎨 资源连接:")
        print(f"  字体URL: {len(resource_conn['font_urls'])} 个")
        print(f"  图片URL: {len(resource_conn['image_urls'])} 个")
        print(f"  外部域名: {len(resource_conn['external_domains'])} 个")
        
        # 显示API连接
        api_conn = result['api_connections']
        print(f"\n🔗 API连接:")
        print(f"  视频API: {len(api_conn['video_apis'])} 个")
        print(f"  数据API: {len(api_conn['data_apis'])} 个")
        print(f"  CDN端点: {len(api_conn['cdn_apis'])} 个")
        
        # 显示详细的连接列表
        print(f"\n📋 详细连接列表:")
        print("-" * 60)
        
        # 页面脚本
        if page_conn['scripts']:
            print(f"\n📜 页面脚本:")
            for i, script in enumerate(page_conn['scripts'], 1):
                print(f"  {i}. {script['url']}")
        
        # 视频URL
        if video_conn['video_urls']:
            print(f"\n🎬 视频URL:")
            for i, video in enumerate(video_conn['video_urls'], 1):
                print(f"  {i}. {video['url']}")
        
        # 流媒体URL
        if video_conn['stream_urls']:
            print(f"\n📺 流媒体URL:")
            for i, stream in enumerate(video_conn['stream_urls'], 1):
                print(f"  {i}. {stream['url']}")
        
        # API端点
        if video_conn['api_endpoints']:
            print(f"\n🔗 API端点:")
            for i, api in enumerate(video_conn['api_endpoints'][:10], 1):  # 只显示前10个
                print(f"  {i}. {api['url']}")
        
        # 外部域名
        if video_conn['external_domains']:
            print(f"\n🌐 外部域名:")
            for i, domain in enumerate(video_conn['external_domains'], 1):
                print(f"  {i}. {domain}")
        
        # 保存结果
        filename = extractor.save_connections(result)
        
    else:
        print(f"\n❌ 提取失败: {result.get('error', '未知错误')}")


if __name__ == "__main__":
    main()
