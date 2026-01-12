#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
使用 Selenium 绕过搜狗反爬虫
真实浏览器环境 + 慢速访问

依赖安装:
    pip install selenium webdriver-manager
    
用法:
    python scraper_selenium.py "公众号名称" [数量]
"""

import sys
import time
import random
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from loguru import logger
from scraper import WeChatScraper

class SeleniumWeChatScraper:
    """使用 Selenium 的微信公众号采集器"""
    
    def __init__(self, headless: bool = False):
        """
        初始化
        
        Args:
            headless: 是否无头模式（False 可以看到浏览器，方便调试）
        """
        self.headless = headless
        self.driver = None
        self.firecrawl_scraper = WeChatScraper()
        
    def init_driver(self):
        """初始化 Selenium WebDriver"""
        try:
            options = ChromeOptions()
            
            if self.headless:
                options.add_argument('--headless')
            
            # 模拟真实浏览器
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # 隐藏 webdriver 特征
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            
            logger.success("Selenium 浏览器初始化成功")
            
        except Exception as e:
            logger.error(f"初始化浏览器失败: {e}")
            raise
    
    def search_articles(self, account_name: str, max_count: int = 10) -> list:
        """
        使用 Selenium 搜索文章
        
        Args:
            account_name: 公众号名称
            max_count: 最大数量
            
        Returns:
            文章列表 [{'title': str, 'url': str, ...}, ...]
        """
        if not self.driver:
            self.init_driver()
        
        articles = []
        page = 1
        base_url = "https://weixin.sogou.com"
        
        logger.info(f"开始搜索: {account_name} (目标 {max_count} 篇)")
        
        while len(articles) < max_count:
            try:
                url = f"{base_url}/weixin?type=2&query={account_name}&page={page}"
                logger.info(f"访问第 {page} 页...")
                
                self.driver.get(url)
                
                # 随机等待，模拟人类行为
                time.sleep(random.uniform(3, 6))
                
                # 检查是否有验证码
                if "antispider" in self.driver.current_url or "验证" in self.driver.page_source:
                    logger.warning("⚠️ 触发验证码！")
                    logger.warning("请在浏览器中手动完成验证，然后按 Enter 继续...")
                    input("完成验证后按 Enter: ")
                    continue
                
                # 解析页面
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                
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
                
                logger.info(f"第 {page} 页找到 {len(news_list)} 个条目")
                
                success_count = 0  # 本页成功数
                fail_count = 0     # 本页失败数
                
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
                        
                        sogou_url = link_elem['href']
                        if sogou_url.startswith('/'):
                            sogou_url = base_url + sogou_url
                        
                        title = link_elem.text.strip()
                        
                        # 关键: 使用 Selenium 跟踪重定向
                        logger.info(f"  跟踪重定向: {title[:30]}...")
                        real_url = self._track_redirect(sogou_url)
                        
                        if not real_url or 'mp.weixin.qq.com' not in real_url:
                            logger.warning(f"  ⚠️ 跳过（无法获取真实URL）")
                            fail_count += 1
                            continue
                        
                        date_elem = news.find('span', class_='s2')
                        date = date_elem.text.strip() if date_elem else ''
                        
                        summary_elem = news.find('p', class_='txt-info')
                        summary = summary_elem.text.strip() if summary_elem else ''
                        
                        articles.append({
                            'title': title,
                            'url': real_url,  # 真实的微信URL
                            'date': date,
                            'summary': summary
                        })
                        
                        success_count += 1
                        logger.success(f"  ✅ {title[:30]}...")
                        
                    except Exception as e:
                        logger.error(f"  解析文章失败: {e}")
                        fail_count += 1
                        continue
                
                # 显示本页统计
                logger.info(f"第 {page} 页完成: 成功 {success_count}/{len(news_list)}, 失败 {fail_count}/{len(news_list)}")
                
                if len(articles) >= max_count:
                    break
                
                # 翻页前等待
                time.sleep(random.uniform(5, 10))
                page += 1
                
            except Exception as e:
                logger.error(f"访问第 {page} 页失败: {e}")
                break
        
        logger.success(f"共找到 {len(articles)} 篇文章（真实URL）")
        return articles
    
    def _track_redirect(self, sogou_url: str) -> str:
        """
        使用 Selenium 跟踪重定向到真实微信URL
        
        Args:
            sogou_url: 搜狗重定向链接
            
        Returns:
            真实的微信文章URL
        """
        try:
            # 在新标签页中打开
            original_window = self.driver.current_window_handle
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            self.driver.get(sogou_url)
            
            # 增加等待时间，让重定向完成
            time.sleep(random.uniform(2, 4))  # 关键：增加随机延迟
            
            # 等待重定向完成
            WebDriverWait(self.driver, 15).until(
                lambda d: 'mp.weixin.qq.com' in d.current_url or 
                          'antispider' in d.current_url or
                          'sogou.com' not in d.current_url
            )
            
            final_url = self.driver.current_url
            
            # 关闭新标签页
            self.driver.close()
            self.driver.switch_to.window(original_window)
            
            if 'mp.weixin.qq.com' in final_url:
                return final_url
            elif 'antispider' in final_url:
                logger.warning(f"  ⚠️  触发验证码，将暂停等待...")
                # 切回主窗口并暂停
                self.driver.switch_to.window(original_window)
                # 打开验证码页面让用户处理
                self.driver.execute_script(f"window.open('{final_url}', '_blank');")
                input("  请在新打开的标签页中完成验证码，然后按 Enter 继续: ")
                # 关闭验证码标签页
                if len(self.driver.window_handles) > 1:
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    self.driver.close()
                    self.driver.switch_to.window(original_window)
                return None
            else:
                return None
                
        except Exception as e:
            logger.warning(f"跟踪重定向失败: {e}")
            # 确保返回原窗口
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                pass
            return None
    
    def run(self, account_name: str, max_count: int = 10):
        """主流程"""
        try:
            # 1. 搜索并获取真实URL
            articles = self.search_articles(account_name, max_count)
            
            if not articles:
                logger.warning("未找到文章")
                return
            
            # 2. 使用 Firecrawl 抓取内容
            logger.info("\n开始抓取文章内容...")
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
                        metadata={
                            'title': article['title'],
                            'url': article['url'],
                            'date': article['date'],
                            'summary': article['summary']
                        }
                    )
                    
                    success += 1
                    logger.success(f"  ✅ 成功 ({len(content)} 字符)")
                    
                    # 抓取间隔
                    time.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    logger.error(f"  ❌ 失败: {e}")
                    fail += 1
            
            logger.info("\n" + "="*60)
            logger.success("抓取完成!")
            logger.info(f"  ✅ 成功: {success} 篇")
            logger.info(f"  ❌ 失败: {fail} 篇")
            logger.info("="*60)
            
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("浏览器已关闭")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    account_name = sys.argv[1]
    max_count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    # headless=False 可以看到浏览器，方便调试和手动验证
    scraper = SeleniumWeChatScraper(headless=False)
    scraper.run(account_name, max_count)
