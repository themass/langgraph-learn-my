#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频页面分析工具
专门用于分析视频网站并提取视频信息
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Optional, Any


class VideoPageAnalyzer:
    """视频页面分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """设置请求会话"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })
    
    def analyze_video_page(self, url: str) -> Dict[str, Any]:
        """
        分析视频页面
        
        Args:
            url: 视频页面URL
            
        Returns:
            包含视频信息的字典
        """
        print(f"🔍 正在分析视频页面: {url}")
        print("=" * 60)
        
        try:
            # 获取页面内容
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            print(f"✅ 页面获取成功")
            print(f"📊 状态码: {response.status_code}")
            print(f"📏 内容长度: {len(response.content)} 字节")
            print(f"🔤 编码: {response.encoding}")
            
            # 解析HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取基本信息
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "无标题"
            
            # 提取meta信息
            meta_description = soup.find('meta', attrs={'name': 'description'})
            description = meta_description.get('content', '').strip() if meta_description else ''
            
            # 提取所有文本内容
            text_content = soup.get_text()
            cleaned_text = ' '.join(text_content.split())
            
            print(f"📄 页面标题: {title_text}")
            print(f"📝 页面描述: {description}")
            print(f"📊 文本长度: {len(cleaned_text)} 字符")
            
            # 分析视频信息
            video_info = self._extract_video_info(soup, url)
            
            # 分析页面结构
            page_structure = self._analyze_page_structure(soup)
            
            # 查找JavaScript中的视频信息
            js_video_info = self._extract_js_video_info(response.text)
            
            # 查找API接口
            api_endpoints = self._find_api_endpoints(response.text, url)
            
            result = {
                'url': url,
                'title': title_text,
                'description': description,
                'content_length': len(response.content),
                'text_content': cleaned_text,
                'video_info': video_info,
                'page_structure': page_structure,
                'js_video_info': js_video_info,
                'api_endpoints': api_endpoints,
                'raw_html': response.text,
                'success': True
            }
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {e}")
            return {'url': url, 'error': str(e), 'success': False}
        except Exception as e:
            print(f"❌ 分析失败: {e}")
            return {'url': url, 'error': str(e), 'success': False}
    
    def _extract_video_info(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """提取视频信息"""
        print("\n🎬 分析视频信息...")
        
        video_info = {
            'video_elements': [],
            'video_sources': [],
            'video_scripts': [],
            'video_urls': [],
            'video_thumbnails': []
        }
        
        # 查找video标签
        videos = soup.find_all('video')
        for i, video in enumerate(videos, 1):
            print(f"  发现video标签 {i}")
            video_data = {
                'src': video.get('src', ''),
                'poster': video.get('poster', ''),
                'controls': video.get('controls'),
                'autoplay': video.get('autoplay'),
                'loop': video.get('loop'),
                'muted': video.get('muted'),
                'width': video.get('width'),
                'height': video.get('height'),
                'sources': []
            }
            
            # 处理相对URL
            if video_data['src']:
                video_data['src'] = urljoin(base_url, video_data['src'])
            if video_data['poster']:
                video_data['poster'] = urljoin(base_url, video_data['poster'])
            
            # 查找source标签
            sources = video.find_all('source')
            for source in sources:
                src = source.get('src', '')
                if src:
                    src = urljoin(base_url, src)
                video_data['sources'].append({
                    'src': src,
                    'type': source.get('type', ''),
                    'media': source.get('media', '')
                })
            
            video_info['video_elements'].append(video_data)
        
        # 查找iframe中的视频
        iframes = soup.find_all('iframe')
        for i, iframe in enumerate(iframes, 1):
            src = iframe.get('src', '')
            if any(domain in src for domain in ['youtube', 'vimeo', 'dailymotion', 'bilibili']):
                print(f"  发现视频iframe {i}: {src}")
                video_info['video_sources'].append({
                    'type': 'iframe',
                    'src': src,
                    'width': iframe.get('width'),
                    'height': iframe.get('height')
                })
        
        # 查找图片中的视频缩略图
        images = soup.find_all('img')
        for img in images:
            src = img.get('src', '')
            alt = img.get('alt', '')
            if any(keyword in alt.lower() for keyword in ['video', 'play', '视频', '播放']):
                print(f"  发现视频缩略图: {src}")
                video_info['video_thumbnails'].append({
                    'src': urljoin(base_url, src),
                    'alt': alt
                })
        
        print(f"  ✅ 找到 {len(video_info['video_elements'])} 个video元素")
        print(f"  ✅ 找到 {len(video_info['video_sources'])} 个视频源")
        print(f"  ✅ 找到 {len(video_info['video_thumbnails'])} 个视频缩略图")
        
        return video_info
    
    def _analyze_page_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """分析页面结构"""
        print("\n🏗️ 分析页面结构...")
        
        structure = {
            'scripts': [],
            'stylesheets': [],
            'forms': [],
            'links': [],
            'meta_tags': []
        }
        
        # 分析脚本
        scripts = soup.find_all('script')
        for script in scripts:
            src = script.get('src', '')
            if src:
                structure['scripts'].append({
                    'src': src,
                    'type': script.get('type', ''),
                    'async': script.get('async'),
                    'defer': script.get('defer')
                })
        
        # 分析样式表
        stylesheets = soup.find_all('link', rel='stylesheet')
        for stylesheet in stylesheets:
            structure['stylesheets'].append({
                'href': stylesheet.get('href', ''),
                'type': stylesheet.get('type', '')
            })
        
        # 分析表单
        forms = soup.find_all('form')
        for form in forms:
            structure['forms'].append({
                'action': form.get('action', ''),
                'method': form.get('method', 'GET'),
                'enctype': form.get('enctype', '')
            })
        
        # 分析链接
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            text = link.get_text().strip()
            if href and text:
                structure['links'].append({
                    'href': href,
                    'text': text
                })
        
        # 分析meta标签
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            name = meta.get('name', '') or meta.get('property', '')
            content = meta.get('content', '')
            if name and content:
                structure['meta_tags'].append({
                    'name': name,
                    'content': content
                })
        
        print(f"  ✅ 找到 {len(structure['scripts'])} 个脚本")
        print(f"  ✅ 找到 {len(structure['stylesheets'])} 个样式表")
        print(f"  ✅ 找到 {len(structure['forms'])} 个表单")
        print(f"  ✅ 找到 {len(structure['links'])} 个链接")
        print(f"  ✅ 找到 {len(structure['meta_tags'])} 个meta标签")
        
        return structure
    
    def _extract_js_video_info(self, html_content: str) -> Dict[str, Any]:
        """从JavaScript中提取视频信息"""
        print("\n🔍 分析JavaScript中的视频信息...")
        
        js_video_info = {
            'video_urls': [],
            'video_configs': [],
            'api_calls': []
        }
        
        # 查找视频URL模式
        video_url_patterns = [
            r'["\']([^"\']*\.(?:mp4|webm|ogg|avi|mov|flv|mkv|m3u8))["\']',
            r'["\']([^"\']*video[^"\']*)["\']',
            r'["\']([^"\']*play[^"\']*)["\']',
            r'src\s*[:=]\s*["\']([^"\']+)["\']',
            r'url\s*[:=]\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in video_url_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                if match and len(match) > 10:  # 过滤太短的匹配
                    js_video_info['video_urls'].append(match)
        
        # 查找视频配置
        config_patterns = [
            r'videoConfig\s*[:=]\s*({[^}]+})',
            r'playerConfig\s*[:=]\s*({[^}]+})',
            r'videoSettings\s*[:=]\s*({[^}]+})'
        ]
        
        for pattern in config_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                try:
                    # 尝试解析JSON
                    config = json.loads(match)
                    js_video_info['video_configs'].append(config)
                except:
                    js_video_info['video_configs'].append(match)
        
        # 查找API调用
        api_patterns = [
            r'fetch\s*\(\s*["\']([^"\']+)["\']',
            r'ajax\s*\(\s*["\']([^"\']+)["\']',
            r'\.get\s*\(\s*["\']([^"\']+)["\']',
            r'\.post\s*\(\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in api_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                if any(keyword in match.lower() for keyword in ['video', 'play', 'stream', 'api']):
                    js_video_info['api_calls'].append(match)
        
        print(f"  ✅ 找到 {len(js_video_info['video_urls'])} 个视频URL")
        print(f"  ✅ 找到 {len(js_video_info['video_configs'])} 个视频配置")
        print(f"  ✅ 找到 {len(js_video_info['api_calls'])} 个API调用")
        
        return js_video_info
    
    def _find_api_endpoints(self, html_content: str, base_url: str) -> List[str]:
        """查找API端点"""
        print("\n🔗 查找API端点...")
        
        api_endpoints = []
        
        # 查找API URL模式
        api_patterns = [
            r'["\']([^"\']*api[^"\']*)["\']',
            r'["\']([^"\']*ajax[^"\']*)["\']',
            r'["\']([^"\']*json[^"\']*)["\']',
            r'["\']([^"\']*data[^"\']*)["\']'
        ]
        
        for pattern in api_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                if match and not match.startswith('http'):
                    # 转换为绝对URL
                    absolute_url = urljoin(base_url, match)
                    api_endpoints.append(absolute_url)
        
        # 去重
        api_endpoints = list(set(api_endpoints))
        
        print(f"  ✅ 找到 {len(api_endpoints)} 个API端点")
        
        return api_endpoints
    
    def save_analysis(self, data: Dict[str, Any], filename: str = None) -> str:
        """保存分析结果"""
        if not filename:
            domain = urlparse(data['url']).netloc
            timestamp = int(time.time())
            filename = f"video_analysis_{domain}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 分析结果已保存到: {filename}")
            return filename
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return ""


def main():
    """主函数"""
    print("视频页面分析工具")
    print("=" * 60)
    
    # 目标URL
    target_url = "https://www.a3m5m.com/s/video/shipin/1044455"
    
    # 创建分析器
    analyzer = VideoPageAnalyzer()
    
    # 分析页面
    result = analyzer.analyze_video_page(target_url)
    
    if result['success']:
        print(f"\n🎉 分析完成!")
        print(f"🌐 URL: {result['url']}")
        print(f"📄 标题: {result['title']}")
        print(f"📝 描述: {result['description']}")
        
        # 显示视频信息
        video_info = result['video_info']
        print(f"\n🎬 视频信息:")
        print(f"  video元素: {len(video_info['video_elements'])} 个")
        print(f"  视频源: {len(video_info['video_sources'])} 个")
        print(f"  视频缩略图: {len(video_info['video_thumbnails'])} 个")
        
        if video_info['video_elements']:
            print(f"\n📹 video元素详情:")
            for i, video in enumerate(video_info['video_elements'], 1):
                print(f"  {i}. src: {video['src']}")
                print(f"     poster: {video['poster']}")
                if video['sources']:
                    print(f"     sources: {len(video['sources'])} 个")
                    for j, source in enumerate(video['sources'], 1):
                        print(f"       {j}. {source['src']} ({source['type']})")
        
        if video_info['video_sources']:
            print(f"\n📺 视频源详情:")
            for i, source in enumerate(video_info['video_sources'], 1):
                print(f"  {i}. {source['type']}: {source['src']}")
        
        # 显示JavaScript中的视频信息
        js_info = result['js_video_info']
        if js_info['video_urls']:
            print(f"\n🔍 JavaScript中的视频URL:")
            for i, url in enumerate(js_info['video_urls'][:10], 1):  # 只显示前10个
                print(f"  {i}. {url}")
        
        if js_info['api_calls']:
            print(f"\n🔗 API调用:")
            for i, api in enumerate(js_info['api_calls'][:10], 1):  # 只显示前10个
                print(f"  {i}. {api}")
        
        # 显示文本内容预览
        if result['text_content']:
            print(f"\n📖 文本内容预览:")
            print("-" * 40)
            preview = result['text_content'][:500]
            print(preview)
            if len(result['text_content']) > 500:
                print("... (内容已截断)")
        
        # 保存分析结果
        filename = analyzer.save_analysis(result)
        
    else:
        print(f"\n❌ 分析失败: {result.get('error', '未知错误')}")


if __name__ == "__main__":
    main()
