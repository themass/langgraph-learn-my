#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
使用 RSSHub 获取微信公众号文章

RSSHub 支持微信公众号订阅，可以自动获取文章URL
官网: https://docs.rsshub.app/routes/new-media#wei-xin

前置条件:
1. 部署 RSSHub 服务（Docker 或公共实例）
2. 获取公众号 ID（biz 参数）

用法:
    python scraper_rsshub.py <公众号biz> [数量]
    
示例:
    python scraper_rsshub.py MzI1NjU2MTU4MA== 10
"""

import sys
import feedparser
from loguru import logger
from scraper import WeChatScraper

class RSSHubScraper:
    """基于 RSSHub 的采集器"""
    
    def __init__(self, rsshub_url: str = "https://rsshub.app"):
        """
        初始化
        
        Args:
            rsshub_url: RSSHub 服务地址（默认使用公共实例）
        """
        self.rsshub_url = rsshub_url.rstrip('/')
        self.firecrawl_scraper = WeChatScraper()
        logger.info(f"RSSHub: {self.rsshub_url}")
    
    def get_articles_from_rss(self, account_biz: str, max_count: int = 10) -> list:
        """
        从 RSS 获取文章列表
        
        Args:
            account_biz: 公众号 biz 参数（从公众号URL中获取）
            max_count: 最大数量
            
        Returns:
            文章列表
        """
        rss_url = f"{self.rsshub_url}/wechat/mp/msgalbum/{account_biz}"
        
        logger.info(f"正在获取 RSS: {rss_url}")
        
        try:
            feed = feedparser.parse(rss_url)
            
            if not feed.entries:
                logger.warning("RSS 没有返回文章")
                logger.warning("可能原因:")
                logger.warning("  1. biz 参数不正确")
                logger.warning("  2. RSSHub 服务不可用")
                logger.warning("  3. 公众号没有开启消息列表")
                return []
            
            articles = []
            for entry in feed.entries[:max_count]:
                articles.append({
                    'title': entry.title,
                    'url': entry.link,  # 真实的微信 URL
                    'date': entry.get('published', ''),
                    'summary': entry.get('summary', '')
                })
            
            logger.success(f"从 RSS 获取到 {len(articles)} 篇文章")
            return articles
            
        except Exception as e:
            logger.error(f"解析 RSS 失败: {e}")
            return []
    
    def run(self, account_biz: str, max_count: int = 10, account_name: str = None):
        """主流程"""
        # 1. 从 RSS 获取文章URL
        articles = self.get_articles_from_rss(account_biz, max_count)
        
        if not articles:
            return
        
        # 2. 使用 Firecrawl 抓取内容
        logger.info("\n开始抓取文章内容...")
        
        if not account_name:
            account_name = f"biz_{account_biz[:10]}"
        
        success = 0
        fail = 0
        
        for idx, article in enumerate(articles, 1):
            logger.info(f"\n[{idx}/{len(articles)}] {article['title'][:50]}...")
            
            try:
                result = self.firecrawl_scraper.scrape_article(article['url'])
                
                if not result or not result.get('markdown'):
                    logger.warning("  ⚠️ 内容为空")
                    fail += 1
                    continue
                
                content = result['markdown']
                
                if len(content) < 200:
                    logger.warning(f"  ⚠️ 内容过短 ({len(content)} 字符)")
                    fail += 1
                    continue
                
                # 保存
                self.firecrawl_scraper.save_markdown(
                    content=content,
                    title=article['title'],
                    source=account_name,
                    metadata=article
                )
                
                success += 1
                logger.success(f"  ✅ 成功 ({len(content)} 字符)")
                
            except Exception as e:
                logger.error(f"  ❌ 失败: {e}")
                fail += 1
        
        logger.info("\n" + "="*60)
        logger.success("抓取完成!")
        logger.info(f"  ✅ 成功: {success} 篇")
        logger.info(f"  ❌ 失败: {fail} 篇")
        logger.info("="*60)


def get_biz_guide():
    """获取 biz 参数的指南"""
    print("""
如何获取公众号的 biz 参数？

方法 1: 从公众号文章URL提取
---------------------------------
1. 在浏览器中打开任意一篇该公众号的文章
2. 查看 URL，找到 __biz 参数
   
   例如: https://mp.weixin.qq.com/s?__biz=MzI1NjU2NTU4MA==&...
                                        ^^^^^^^^^^^^^^^^
                                        这就是 biz 参数

方法 2: 使用 RSSHub 的搜索功能
---------------------------------
访问: https://docs.rsshub.app/routes/new-media#wei-xin
查看文档中关于如何获取 biz 的说明

方法 3: 浏览器开发者工具
---------------------------------
1. 打开公众号历史文章页面
2. F12 打开开发者工具
3. Network 标签查看请求
4. 找到包含 __biz 的请求URL
""")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help', 'help']:
        print(__doc__)
        get_biz_guide()
        sys.exit(0 if len(sys.argv) > 1 else 1)
    
    account_biz = sys.argv[1]
    max_count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    account_name = sys.argv[3] if len(sys.argv) > 3 else None
    
    scraper = RSSHubScraper()
    scraper.run(account_biz, max_count, account_name)
