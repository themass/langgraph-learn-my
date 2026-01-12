#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
微信公众号文章采集器
输入公众号名称，自动搜索并抓取文章
"""

import requests
from bs4 import BeautifulSoup
from firecrawl import FirecrawlApp
from pathlib import Path
from loguru import logger
import re
import sys
import time
import random


class Config:
    """配置"""
    FIRECRAWL_URL = "http://localhost:3002"
    OUTPUT_DIR = Path("articles")
    

class WeChatScraper:
    """微信公众号文章采集器"""
    
    def __init__(self):
        """初始化"""
        self.base_url = "https://weixin.sogou.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://weixin.sogou.com/'
        }
        
        # 初始化 Firecrawl
        self.firecrawl = FirecrawlApp(api_url=Config.FIRECRAWL_URL)
        self.output_dir = Config.OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        logger.info(f"采集器初始化完成 (Firecrawl: {Config.FIRECRAWL_URL})")
        logger.info(f"输出目录: {self.output_dir.absolute()}")
    
    def search_articles(self, account_name: str, max_count: int = 10) -> list:
        """
        搜索公众号文章
        
        Args:
            account_name: 公众号名称
            max_count: 最大抓取数量
            
        Returns:
            文章列表 [{'title': str, 'url': str, 'date': str, 'summary': str}, ...]
        """
        articles = []
        page = 1
        
        logger.info(f"正在搜索公众号: {account_name} (最多 {max_count} 篇)")
        
        while len(articles) < max_count:
            try:
                url = f"{self.base_url}/weixin?type=2&query={account_name}&page={page}"
                logger.info(f"正在抓取第 {page} 页...")
                
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 正确的解析方式：找到 news-list 中的所有 li
                news_box = soup.find('div', class_='news-box')
                if not news_box:
                    logger.info(f"第 {page} 页没有找到 news-box")
                    break
                
                news_list_ul = news_box.find('ul', class_='news-list')
                if not news_list_ul:
                    logger.info(f"第 {page} 页没有找到 news-list")
                    break
                
                news_list = news_list_ul.find_all('li')
                
                if not news_list:
                    logger.info(f"第 {page} 页没有更多文章")
                    break
                
                for news in news_list:
                    if len(articles) >= max_count:
                        break
                    
                    try:
                        title_elem = news.find('h3')
                        if not title_elem:
                            continue
                        
                        link_elem = title_elem.find('a')
                        if not link_elem or 'href' not in link_elem.attrs:
                            continue
                        
                        url = link_elem['href']
                        if url.startswith('/'):
                            url = self.base_url + url
                        
                        title = link_elem.text.strip()
                        
                        date_elem = news.find('span', class_='s2')
                        date = date_elem.text.strip() if date_elem else ''
                        
                        summary_elem = news.find('p', class_='txt-info')
                        summary = summary_elem.text.strip() if summary_elem else ''
                        
                        articles.append({
                            'title': title,
                            'url': url,
                            'date': date,
                            'summary': summary
                        })
                        
                        logger.debug(f"找到文章: {title}")
                        
                    except Exception as e:
                        logger.error(f"解析文章失败: {e}")
                        continue
                
                page += 1
                
                # 随机延迟，避免被封
                if len(articles) < max_count:
                    delay = random.uniform(3, 6)
                    logger.debug(f"延迟 {delay:.1f} 秒...")
                    time.sleep(delay)
                
            except Exception as e:
                logger.error(f"搜索失败: {e}")
                break
        
        logger.success(f"共找到 {len(articles)} 篇文章")
        return articles
    
    def scrape_article(self, url: str) -> dict:
        """
        使用 Firecrawl 抓取文章
        
        Args:
            url: 文章 URL
            
        Returns:
            {'markdown': str, 'html': str, 'metadata': dict, 'images': list}
        """
        try:
            # 如果是搜狗重定向链接，尝试跟踪
            if 'weixin.sogou.com/link' in url:
                logger.debug("检测到搜狗重定向链接，尝试跟踪...")
                try:
                    # 方法1: 使用 requests 跟踪重定向
                    session = requests.Session()
                    session.headers.update(self.headers)
                    response = session.get(url, timeout=10, allow_redirects=True)
                    final_url = response.url
                    
                    if 'mp.weixin.qq.com' in final_url:
                        url = final_url
                        logger.success(f"✅ 重定向成功: {url[:80]}...")
                    else:
                        # 方法2: 尝试从 HTML 中提取真实链接
                        soup = BeautifulSoup(response.text, 'html.parser')
                        # 查找可能的跳转链接
                        meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
                        if meta_refresh and 'content' in meta_refresh.attrs:
                            content = meta_refresh['content']
                            if 'url=' in content:
                                redirect_url = content.split('url=')[1]
                                if 'mp.weixin.qq.com' in redirect_url:
                                    url = redirect_url
                                    logger.success(f"✅ 从 meta 标签获取到真实 URL: {url[:80]}...")
                        
                        # 如果还是搜狗链接，记录警告
                        if 'mp.weixin.qq.com' not in url:
                            logger.warning(f"⚠️ 无法跟踪到真实 URL，将尝试直接抓取搜狗链接")
                            logger.warning(f"   最终 URL: {final_url[:100]}")
                except Exception as e:
                    logger.warning(f"⚠️ 重定向跟踪失败: {e}")
            
            logger.info(f"正在抓取: {url[:80]}...")
            
            result = self.firecrawl.scrape(
                url=url,
                formats=['markdown', 'html'],
                only_main_content=True,
                include_tags=['article', 'main', 'div.rich_media_content', 'div#js_content'],
                exclude_tags=['nav', 'footer', 'aside', 'script', 'style', 'iframe'],
                wait_for=5000,  # 增加等待时间到 5 秒
                remove_base64_images=False
            )
            
            if not result:
                logger.error("❌ Firecrawl 返回空结果")
                return None
            
            # 提取数据
            markdown = result.markdown if hasattr(result, 'markdown') else ''
            html = result.html if hasattr(result, 'html') else ''
            metadata_obj = result.metadata if hasattr(result, 'metadata') else None
            
            # 检查内容是否过短（可能是错误页面）
            content_length = len(markdown) if markdown else len(html)
            if content_length < 100:
                logger.warning(f"⚠️ 内容过短 ({content_length} 字符)，可能不是真实文章")
                logger.warning(f"   URL: {url[:100]}")
                # 仍然返回结果，让调用者决定是否保存
            
            metadata = {}
            if metadata_obj:
                metadata = {
                    'title': metadata_obj.title,
                    'description': metadata_obj.description,
                    'url': metadata_obj.url,
                }
            
            return {
                'markdown': markdown or '',
                'html': html or '',
                'metadata': metadata,
                'images': result.images if hasattr(result, 'images') and result.images else []
            }
            
        except Exception as e:
            logger.error(f"抓取失败: {e}")
            return None
    
    def save_markdown(self, content: str, title: str, source: str, metadata: dict = None) -> str:
        """保存 Markdown 文件"""
        safe_title = self._sanitize_filename(title)
        safe_source = self._sanitize_filename(source)
        
        source_dir = self.output_dir / safe_source
        source_dir.mkdir(exist_ok=True, parents=True)
        
        file_path = source_dir / f"{safe_title}.md"
        
        counter = 1
        while file_path.exists():
            file_path = source_dir / f"{safe_title}_{counter}.md"
            counter += 1
        
        # 添加头部
        if metadata:
            header = f"# {title}\n\n"
            if metadata.get('url'):
                header += f"**原文链接**: {metadata['url']}\n"
            if metadata.get('date'):
                header += f"**发布时间**: {metadata['date']}\n"
            if metadata.get('summary'):
                header += f"**摘要**: {metadata['summary']}\n"
            header += "\n---\n\n"
            content = header + content
        
        try:
            file_path.write_text(content, encoding='utf-8')
            logger.success(f"已保存: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"保存失败: {e}")
            return ""
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名"""
        filename = re.sub(r'[\\/*?:"<>|]', "", filename)
        return filename.strip()[:100] if filename else "untitled"
    
    def run(self, account_name: str, max_count: int = 10):
        """
        运行采集器
        
        Args:
            account_name: 公众号名称
            max_count: 最大抓取数量
        """
        logger.info("=" * 60)
        logger.info(f"开始抓取公众号: {account_name}")
        logger.info(f"目标数量: {max_count} 篇")
        logger.info("=" * 60)
        
        # 1. 搜索文章列表
        articles = self.search_articles(account_name, max_count)
        
        if not articles:
            logger.error("没有找到文章")
            return
        
        # 2. 逐个抓取
        success_count = 0
        failed_count = 0
        
        logger.info(f"\n开始抓取文章内容...")
        
        for idx, article in enumerate(articles, 1):
            logger.info(f"\n[{idx}/{len(articles)}] {article['title'][:50]}")
            
            try:
                # 抓取内容
                result = self.scrape_article(article['url'])
                
                if not result or (not result['markdown'] and not result['html']):
                    logger.warning("⚠️ 内容为空，跳过")
                    failed_count += 1
                    continue
                
                # 保存
                content = result['markdown'] if result['markdown'] else result['html']
                
                # 检查内容质量
                if len(content) < 200:
                    logger.warning(f"⚠️ 内容过短 ({len(content)} 字符)，可能是搜狗重定向问题")
                    logger.warning(f"💡 提示: 搜狗反爬虫导致无法获取真实内容")
                    # 仍然保存，但标记为失败
                    failed_count += 1
                    # 继续处理下一篇
                    continue
                
                metadata = {
                    'url': result['metadata'].get('url', article['url']),
                    'date': article['date'],
                    'summary': article['summary']
                }
                
                file_path = self.save_markdown(
                    content=content,
                    title=article['title'],
                    source=account_name,
                    metadata=metadata
                )
                
                if file_path:
                    logger.info(f"✅ 内容长度: {len(content)} 字符")
                    logger.info(f"✅ 图片数: {len(result['images'])}")
                    success_count += 1
                else:
                    failed_count += 1
                
                # 延迟
                if idx < len(articles):
                    time.sleep(2)
                
            except Exception as e:
                logger.error(f"处理失败: {e}")
                failed_count += 1
        
        # 总结
        logger.info("\n" + "=" * 60)
        logger.success(f"抓取完成!")
        logger.info(f"✅ 成功: {success_count} 篇")
        logger.info(f"❌ 失败: {failed_count} 篇")
        logger.info(f"📁 保存位置: {self.output_dir / account_name}")
        logger.info("=" * 60)


def main():
    """主函数"""
    
    # 配置日志
    logger.add("logs/scraper_{time}.log", rotation="10 MB", retention="7 days")
    
    print("\n" + "=" * 60)
    print("微信公众号文章采集器")
    print("=" * 60)
    print()
    
    if len(sys.argv) >= 2:
        account_name = sys.argv[1]
        max_count = int(sys.argv[2]) if len(sys.argv) >= 3 else 10
    else:
        print("用法:")
        print("  python scraper.py <公众号名称> [抓取数量]")
        print()
        print("示例:")
        print("  python scraper.py Python之禅 10")
        print("  python scraper.py 逛逛GitHub 20")
        print()
        return
    
    # 运行采集器
    scraper = WeChatScraper()
    scraper.run(account_name, max_count)


if __name__ == "__main__":
    main()
