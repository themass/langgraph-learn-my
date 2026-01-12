#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级网页内容获取工具
专门用于处理有反爬虫保护的网站
"""

import requests
from bs4 import BeautifulSoup
import time
import random
import urllib.parse
from typing import Optional, Dict, Any, List
import json


class AdvancedWebScraper:
    """高级网页爬虫"""
    
    def __init__(self):
        """初始化爬虫"""
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """设置session配置"""
        # 设置更真实的请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
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
        
        # 设置重试策略
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _get_random_delay(self, min_delay: float = 1.0, max_delay: float = 3.0) -> float:
        """获取随机延迟时间"""
        return random.uniform(min_delay, max_delay)
    
    def _simulate_human_behavior(self):
        """模拟人类行为"""
        delay = self._get_random_delay()
        print(f"模拟人类行为，等待 {delay:.1f} 秒...")
        time.sleep(delay)
    
    def _try_multiple_user_agents(self, url: str, timeout: int = 30) -> Optional[requests.Response]:
        """尝试多种User-Agent"""
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        ]
        
        for i, ua in enumerate(user_agents, 1):
            print(f"尝试User-Agent {i}/{len(user_agents)}...")
            try:
                headers = self.session.headers.copy()
                headers['User-Agent'] = ua
                response = requests.get(url, headers=headers, timeout=timeout)
                if response.status_code == 200:
                    print(f"✅ User-Agent {i} 成功!")
                    return response
                else:
                    print(f"❌ User-Agent {i} 失败: {response.status_code}")
            except Exception as e:
                print(f"❌ User-Agent {i} 异常: {e}")
            
            if i < len(user_agents):
                time.sleep(self._get_random_delay(0.5, 1.5))
        
        return None
    
    def _try_with_referer(self, url: str, timeout: int = 30) -> Optional[requests.Response]:
        """尝试带Referer的请求"""
        try:
            # 解析URL获取域名
            parsed_url = urllib.parse.urlparse(url)
            domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            headers = self.session.headers.copy()
            headers['Referer'] = domain
            headers['Origin'] = domain
            
            print(f"尝试带Referer请求: {domain}")
            response = requests.get(url, headers=headers, timeout=timeout)
            if response.status_code == 200:
                print("✅ 带Referer请求成功!")
                return response
            else:
                print(f"❌ 带Referer请求失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 带Referer请求异常: {e}")
        
        return None
    
    def _try_with_cookies(self, url: str, timeout: int = 30) -> Optional[requests.Response]:
        """尝试带Cookie的请求"""
        try:
            # 先访问主页获取Cookie
            parsed_url = urllib.parse.urlparse(url)
            domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            print(f"先访问主页获取Cookie: {domain}")
            home_response = requests.get(domain, headers=self.session.headers, timeout=timeout)
            
            if home_response.status_code == 200:
                # 使用获取到的Cookie访问目标页面
                cookies = home_response.cookies
                print("✅ 成功获取Cookie，尝试访问目标页面...")
                
                response = requests.get(url, headers=self.session.headers, cookies=cookies, timeout=timeout)
                if response.status_code == 200:
                    print("✅ 带Cookie请求成功!")
                    return response
                else:
                    print(f"❌ 带Cookie请求失败: {response.status_code}")
            else:
                print(f"❌ 获取Cookie失败: {home_response.status_code}")
        except Exception as e:
            print(f"❌ 带Cookie请求异常: {e}")
        
        return None
    
    def scrape_url(self, url: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
        """
        爬取指定URL的内容
        
        Args:
            url: 目标URL
            timeout: 超时时间
            
        Returns:
            包含网页信息的字典
        """
        print(f"开始爬取: {url}")
        print("=" * 50)
        
        # 模拟人类行为
        self._simulate_human_behavior()
        
        # 尝试多种策略
        strategies = [
            ("多种User-Agent", self._try_multiple_user_agents),
            ("带Referer请求", self._try_with_referer),
            ("带Cookie请求", self._try_with_cookies),
            ("Session请求", lambda u, t: self.session.get(u, timeout=t)),
        ]
        
        response = None
        successful_strategy = None
        
        for strategy_name, strategy_func in strategies:
            print(f"\n🔄 尝试策略: {strategy_name}")
            try:
                response = strategy_func(url, timeout)
                if response and response.status_code == 200:
                    successful_strategy = strategy_name
                    print(f"✅ 策略 '{strategy_name}' 成功!")
                    break
                else:
                    print(f"❌ 策略 '{strategy_name}' 失败")
            except Exception as e:
                print(f"❌ 策略 '{strategy_name}' 异常: {e}")
            
            # 策略间延迟
            if strategy_name != strategies[-1][0]:  # 不是最后一个策略
                time.sleep(self._get_random_delay(1, 2))
        
        if not response or response.status_code != 200:
            print("\n❌ 所有策略都失败了")
            return None
        
        # 解析响应内容
        return self._parse_response(response, url, successful_strategy)
    
    def _parse_response(self, response: requests.Response, url: str, strategy: str) -> Dict[str, Any]:
        """解析响应内容"""
        try:
            print(f"\n📊 解析响应内容...")
            
            # 基本信息
            content_type = response.headers.get('content-type', '')
            encoding = response.encoding or 'utf-8'
            
            print(f"状态码: {response.status_code}")
            print(f"内容类型: {content_type}")
            print(f"编码: {encoding}")
            print(f"内容长度: {len(response.content)} 字节")
            
            # 解析HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取标题
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "无标题"
            
            # 提取meta描述
            meta_description = soup.find('meta', attrs={'name': 'description'})
            description = meta_description.get('content', '').strip() if meta_description else ''
            
            # 提取所有文本
            text_content = soup.get_text()
            cleaned_text = ' '.join(text_content.split())
            
            # 提取链接
            links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                text = link.get_text().strip()
                if href and text:
                    if href.startswith('/'):
                        href = urllib.parse.urljoin(url, href)
                    elif not href.startswith(('http://', 'https://')):
                        href = urllib.parse.urljoin(url, href)
                    links.append({'url': href, 'text': text})
            
            # 提取图片
            images = []
            for img in soup.find_all('img', src=True):
                src = img.get('src')
                alt = img.get('alt', '')
                if src:
                    if src.startswith('/'):
                        src = urllib.parse.urljoin(url, src)
                    elif not src.startswith(('http://', 'https://')):
                        src = urllib.parse.urljoin(url, src)
                    images.append({'url': src, 'alt': alt})
            
            result = {
                'url': url,
                'strategy': strategy,
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
            
            print(f"✅ 内容解析完成!")
            return result
            
        except Exception as e:
            print(f"❌ 解析响应时发生错误: {e}")
            return {
                'url': url,
                'strategy': strategy,
                'status_code': response.status_code,
                'error': str(e),
                'success': False
            }
    
    def save_to_file(self, data: Dict[str, Any], filename: str = None) -> str:
        """保存数据到文件"""
        if not filename:
            domain = urllib.parse.urlparse(data['url']).netloc
            timestamp = int(time.time())
            filename = f"scraped_{domain}_{timestamp}.json"
        
        try:
            # 保存为JSON格式
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 数据已保存到: {filename}")
            return filename
        except Exception as e:
            print(f"❌ 保存文件失败: {e}")
            return ""


def main():
    """主函数"""
    # 目标URL
    target_url = "https://hsex.men/video-1131562.htm"
    
    print("高级网页内容获取工具")
    print("=" * 60)
    
    # 创建爬虫
    scraper = AdvancedWebScraper()
    
    # 爬取内容
    result = scraper.scrape_url(target_url)
    
    if result and result['success']:
        print(f"\n🎉 爬取成功!")
        print(f"🌐 URL: {result['url']}")
        print(f"🔧 成功策略: {result['strategy']}")
        print(f"📄 标题: {result['title']}")
        print(f"📝 描述: {result['description']}")
        print(f"🔗 链接数量: {len(result['links'])}")
        print(f"🖼️ 图片数量: {len(result['images'])}")
        print(f"📊 文本长度: {len(result['text_content'])} 字符")
        
        # 显示文本预览
        if result['text_content']:
            print(f"\n📖 文本内容预览:")
            print("-" * 40)
            preview = result['text_content'][:300]
            print(preview)
            if len(result['text_content']) > 300:
                print("... (内容已截断)")
        
        # 保存结果
        filename = scraper.save_to_file(result)
        
        # 显示部分链接
        if result['links']:
            print(f"\n🔗 链接预览 (前5个):")
            print("-" * 40)
            for i, link in enumerate(result['links'][:5], 1):
                print(f"{i}. {link['text'][:30]}... -> {link['url']}")
    
    else:
        print("\n❌ 爬取失败")
        if result:
            print(f"错误信息: {result.get('error', '未知错误')}")


if __name__ == "__main__":
    main()
