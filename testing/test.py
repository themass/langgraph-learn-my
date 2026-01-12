#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网页内容获取工具
用于获取指定URL的网页内容
"""

import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
from typing import Optional, Dict, Any


class WebContentFetcher:
    """网页内容获取器"""
    
    def __init__(self):
        """初始化获取器"""
        self.session = requests.Session()
        # 设置请求头，模拟真实浏览器
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
            'DNT': '1',
        })
        
        # 设置重试和超时
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _fetch_with_session(self, url: str, timeout: int) -> requests.Response:
        """使用session获取内容"""
        return self.session.get(url, timeout=timeout)
    
    def _fetch_with_direct_request(self, url: str, timeout: int) -> requests.Response:
        """使用直接请求获取内容"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        return requests.get(url, headers=headers, timeout=timeout)
    
    def _fetch_with_different_headers(self, url: str, timeout: int) -> requests.Response:
        """使用不同的请求头获取内容"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        return requests.get(url, headers=headers, timeout=timeout)
    
    def fetch_content(self, url: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
        """
        获取网页内容
        
        Args:
            url: 目标URL
            timeout: 超时时间（秒）
            
        Returns:
            包含网页信息的字典，失败时返回None
        """
        try:
            print(f"正在获取网页内容: {url}")
            
            # 添加随机延迟，模拟人类行为
            import random
            delay = random.uniform(1, 3)
            print(f"等待 {delay:.1f} 秒...")
            time.sleep(delay)
            
            # 尝试多种策略获取内容
            strategies = [
                self._fetch_with_session,
                self._fetch_with_direct_request,
                self._fetch_with_different_headers
            ]
            
            for i, strategy in enumerate(strategies, 1):
                print(f"尝试策略 {i}/{len(strategies)}...")
                try:
                    response = strategy(url, timeout)
                    if response and response.status_code == 200:
                        break
                except Exception as e:
                    print(f"策略 {i} 失败: {e}")
                    if i < len(strategies):
                        time.sleep(2)  # 策略间延迟
                    continue
            else:
                print("所有策略都失败了")
                return None
            
            response.raise_for_status()  # 检查HTTP错误
            
            # 获取响应信息
            content_type = response.headers.get('content-type', '')
            encoding = response.encoding or 'utf-8'
            
            print(f"响应状态码: {response.status_code}")
            print(f"内容类型: {content_type}")
            print(f"编码: {encoding}")
            print(f"内容长度: {len(response.content)} 字节")
            
            # 解析HTML内容
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取基本信息
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "无标题"
            
            # 提取meta信息
            meta_description = soup.find('meta', attrs={'name': 'description'})
            description = meta_description.get('content', '') if meta_description else ''
            
            # 提取所有文本内容
            text_content = soup.get_text()
            # 清理文本，移除多余空白
            cleaned_text = ' '.join(text_content.split())
            
            # 提取所有链接
            links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                text = link.get_text().strip()
                if href and text:
                    # 处理相对链接
                    if href.startswith('/'):
                        href = urllib.parse.urljoin(url, href)
                    elif not href.startswith(('http://', 'https://')):
                        href = urllib.parse.urljoin(url, href)
                    links.append({'url': href, 'text': text})
            
            # 提取图片链接
            images = []
            for img in soup.find_all('img', src=True):
                src = img.get('src')
                alt = img.get('alt', '')
                if src:
                    # 处理相对链接
                    if src.startswith('/'):
                        src = urllib.parse.urljoin(url, src)
                    elif not src.startswith(('http://', 'https://')):
                        src = urllib.parse.urljoin(url, src)
                    images.append({'url': src, 'alt': alt})
            
            result = {
                'url': url,
                'status_code': response.status_code,
                'title': title_text,
                'description': description,
                'content_type': content_type,
                'encoding': encoding,
                'content_length': len(response.content),
                'text_content': cleaned_text,
                'links': links,
                'images': images,
                'raw_html': response.text,
                'success': True
            }
            
            print(f"✅ 成功获取网页内容")
            return result
            
        except requests.exceptions.Timeout:
            print(f"❌ 请求超时: {url}")
            return None
        except requests.exceptions.ConnectionError:
            print(f"❌ 连接错误: {url}")
            return None
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP错误: {e}")
            return None
        except Exception as e:
            print(f"❌ 获取内容时发生错误: {e}")
            return None
    
    def save_content(self, content_data: Dict[str, Any], filename: str = None) -> str:
        """
        保存内容到文件
        
        Args:
            content_data: 内容数据
            filename: 文件名，如果为None则自动生成
            
        Returns:
            保存的文件路径
        """
        if not filename:
            # 从URL生成文件名
            url = content_data['url']
            domain = urllib.parse.urlparse(url).netloc
            timestamp = int(time.time())
            filename = f"web_content_{domain}_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"网页内容获取结果\n")
                f.write(f"=" * 50 + "\n\n")
                f.write(f"URL: {content_data['url']}\n")
                f.write(f"状态码: {content_data['status_code']}\n")
                f.write(f"标题: {content_data['title']}\n")
                f.write(f"描述: {content_data['description']}\n")
                f.write(f"内容类型: {content_data['content_type']}\n")
                f.write(f"编码: {content_data['encoding']}\n")
                f.write(f"内容长度: {content_data['content_length']} 字节\n\n")
                
                f.write(f"文本内容:\n")
                f.write("-" * 30 + "\n")
                f.write(content_data['text_content'][:2000])  # 限制文本长度
                if len(content_data['text_content']) > 2000:
                    f.write("\n\n... (内容已截断)")
                f.write("\n\n")
                
                f.write(f"链接列表 (共{len(content_data['links'])}个):\n")
                f.write("-" * 30 + "\n")
                for i, link in enumerate(content_data['links'][:20], 1):  # 限制链接数量
                    f.write(f"{i}. {link['text']} -> {link['url']}\n")
                if len(content_data['links']) > 20:
                    f.write(f"... (还有{len(content_data['links']) - 20}个链接)\n")
                f.write("\n")
                
                f.write(f"图片列表 (共{len(content_data['images'])}个):\n")
                f.write("-" * 30 + "\n")
                for i, img in enumerate(content_data['images'][:10], 1):  # 限制图片数量
                    f.write(f"{i}. {img['alt']} -> {img['url']}\n")
                if len(content_data['images']) > 10:
                    f.write(f"... (还有{len(content_data['images']) - 10}个图片)\n")
            
            print(f"✅ 内容已保存到: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ 保存文件时发生错误: {e}")
            return ""


def main():
    """主函数"""
    # 目标URL列表，包括主要目标和备用测试URL
    target_urls = [
        "https://hsex.men/video-1131562.htm",
        "https://httpbin.org/html",  # 测试URL
        "https://example.com",       # 简单测试URL
    ]
    
    print("网页内容获取工具")
    print("=" * 50)
    
    # 创建获取器
    fetcher = WebContentFetcher()
    
    # 尝试获取内容
    content = None
    successful_url = None
    
    for i, url in enumerate(target_urls, 1):
        print(f"\n尝试URL {i}/{len(target_urls)}: {url}")
        content = fetcher.fetch_content(url)
        if content and content['success']:
            successful_url = url
            break
        else:
            print(f"URL {i} 获取失败，尝试下一个...")
    
    if not content or not content['success']:
        print("\n❌ 所有URL都无法访问")
        print("可能的原因:")
        print("1. 网站有反爬虫保护")
        print("2. 需要登录或特殊权限")
        print("3. 网络连接问题")
        print("4. 网站暂时不可用")
        return
    
    if content and content['success']:
        print(f"\n✅ 成功获取网页内容!")
        print(f"🌐 成功URL: {successful_url}")
        print(f"📄 网页标题: {content['title']}")
        print(f"📝 描述: {content['description']}")
        print(f"🔗 链接数量: {len(content['links'])}")
        print(f"🖼️ 图片数量: {len(content['images'])}")
        print(f"📊 文本长度: {len(content['text_content'])} 字符")
        
        # 显示部分文本内容
        print(f"\n📖 文本内容预览:")
        print("-" * 30)
        preview = content['text_content'][:500]
        print(preview)
        if len(content['text_content']) > 500:
            print("... (内容已截断)")
        
        # 保存到文件
        filename = fetcher.save_content(content)
        if filename:
            print(f"\n💾 完整内容已保存到文件: {filename}")
        
        # 显示部分链接
        if content['links']:
            print(f"\n🔗 链接预览 (前5个):")
            print("-" * 30)
            for i, link in enumerate(content['links'][:5], 1):
                print(f"{i}. {link['text'][:50]}... -> {link['url']}")
    
    else:
        print("❌ 获取网页内容失败")


if __name__ == "__main__":
    main()
