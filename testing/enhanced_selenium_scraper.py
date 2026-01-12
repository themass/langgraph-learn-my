#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版Selenium网页内容获取工具
专门处理Cloudflare验证页面
"""

import time
import json
import random
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import os


class EnhancedSeleniumScraper:
    """增强版Selenium爬虫，专门处理验证页面"""
    
    def __init__(self, headless: bool = False, wait_time: int = 60):
        """
        初始化增强版爬虫
        
        Args:
            headless: 是否使用无头模式
            wait_time: 等待验证完成的最大时间（秒）
        """
        self.headless = headless
        self.wait_time = wait_time
        self.driver = None
        self._setup_driver()
    
    def _setup_driver(self):
        """设置Selenium WebDriver"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import TimeoutException, WebDriverException
            
            # 导入异常类
            self.TimeoutException = TimeoutException
            self.WebDriverException = WebDriverException
            self.By = By
            self.EC = EC
            
            # 设置Chrome选项
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument('--headless')
            
            # 反检测选项
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 设置用户代理
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # 启用图片加载（验证页面可能需要）
            prefs = {
                "profile.managed_default_content_settings.images": 1,
                "profile.default_content_setting_values.notifications": 2
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # 创建WebDriver
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # 执行反检测脚本
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✅ 增强版Selenium WebDriver 初始化成功")
            
        except ImportError:
            print("❌ 请安装selenium: pip install selenium")
            raise
        except Exception as e:
            print(f"❌ WebDriver 初始化失败: {e}")
            raise
    
    def _wait_for_verification(self, timeout: int = 60) -> bool:
        """等待Cloudflare验证完成"""
        print(f"⏳ 等待Cloudflare验证完成（最多{timeout}秒）...")
        
        start_time = time.time()
        last_title = ""
        
        while time.time() - start_time < timeout:
            try:
                current_title = self.driver.title
                current_url = self.driver.current_url
                
                # 检查标题是否改变（验证完成通常标题会改变）
                if current_title != last_title and current_title != "请稍候…":
                    print(f"✅ 检测到标题变化: {current_title}")
                    return True
                
                # 检查URL是否改变（验证完成后可能会重定向）
                if "challenge" not in current_url and "cf-chl" not in current_url:
                    print(f"✅ 检测到URL变化: {current_url}")
                    return True
                
                # 检查页面内容是否包含成功标识
                page_source = self.driver.page_source
                if "验证成功" in page_source or "challenge-success" in page_source:
                    print("✅ 检测到验证成功标识")
                    return True
                
                # 检查是否还有验证相关元素
                try:
                    challenge_elements = self.driver.find_elements(self.By.CSS_SELECTOR, "[id*='challenge'], [class*='challenge'], [id*='cf-chl']")
                    if not challenge_elements:
                        print("✅ 验证元素消失，可能验证完成")
                        return True
                except:
                    pass
                
                last_title = current_title
                time.sleep(2)  # 每2秒检查一次
                
            except Exception as e:
                print(f"⚠️ 检查验证状态时出错: {e}")
                time.sleep(2)
        
        print(f"⏰ 等待超时（{timeout}秒），继续处理当前页面")
        return False
    
    def _simulate_human_behavior(self):
        """模拟人类行为"""
        # 随机滚动
        scroll_height = random.randint(100, 500)
        self.driver.execute_script(f"window.scrollBy(0, {scroll_height});")
        time.sleep(random.uniform(0.5, 1.5))
        
        # 随机移动鼠标
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(self.driver)
            actions.move_by_offset(random.randint(10, 100), random.randint(10, 100))
            actions.perform()
        except:
            pass
        
        time.sleep(random.uniform(1.0, 2.0))
    
    def scrape_with_verification(self, url: str) -> Optional[Dict[str, Any]]:
        """
        爬取需要验证的网页内容
        
        Args:
            url: 目标URL
            
        Returns:
            包含网页信息的字典
        """
        if not self.driver:
            print("❌ WebDriver 未初始化")
            return None
        
        try:
            print(f"🌐 正在访问: {url}")
            
            # 访问页面
            self.driver.get(url)
            
            # 等待页面加载
            print("⏳ 等待页面初始加载...")
            time.sleep(3)
            
            # 模拟人类行为
            self._simulate_human_behavior()
            
            # 检查是否是验证页面
            page_source = self.driver.page_source.lower()
            if any(keyword in page_source for keyword in ['cloudflare', 'challenge', 'verification', '验证']):
                print("🛡️ 检测到Cloudflare验证页面")
                
                # 等待验证完成
                verification_completed = self._wait_for_verification(self.wait_time)
                
                if verification_completed:
                    print("✅ 验证完成，获取最终内容")
                    time.sleep(3)  # 等待页面完全加载
                else:
                    print("⚠️ 验证未完成，获取当前内容")
            else:
                print("✅ 无需验证，直接获取内容")
            
            # 获取最终页面信息
            result = self._extract_page_data(url)
            
            if result:
                print("✅ 内容提取成功")
                return result
            else:
                print("❌ 内容提取失败")
                return None
                
        except self.WebDriverException as e:
            print(f"❌ WebDriver 错误: {e}")
            return None
        except Exception as e:
            print(f"❌ 爬取过程中发生错误: {e}")
            return None
    
    def _extract_page_data(self, url: str) -> Optional[Dict[str, Any]]:
        """提取页面数据"""
        try:
            # 获取基本信息
            title = self.driver.title
            current_url = self.driver.current_url
            
            # 获取页面源码
            page_source = self.driver.page_source
            
            # 使用BeautifulSoup解析
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(page_source, 'html.parser')
                
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
                            href = f"{urlparse(url).scheme}://{urlparse(url).netloc}{href}"
                        elif not href.startswith(('http://', 'https://')):
                            href = f"{urlparse(url).scheme}://{urlparse(url).netloc}/{href}"
                        links.append({'url': href, 'text': text})
                
                # 提取图片
                images = []
                for img in soup.find_all('img', src=True):
                    src = img.get('src')
                    alt = img.get('alt', '')
                    if src:
                        if src.startswith('/'):
                            src = f"{urlparse(url).scheme}://{urlparse(url).netloc}{src}"
                        elif not src.startswith(('http://', 'https://')):
                            src = f"{urlparse(url).scheme}://{urlparse(url).netloc}/{src}"
                        images.append({'url': src, 'alt': alt})
                
                # 提取视频元素
                videos = []
                for video in soup.find_all('video'):
                    src = video.get('src')
                    poster = video.get('poster', '')
                    if src:
                        if src.startswith('/'):
                            src = f"{urlparse(url).scheme}://{urlparse(url).netloc}{src}"
                        elif not src.startswith(('http://', 'https://')):
                            src = f"{urlparse(url).scheme}://{urlparse(url).netloc}/{src}"
                        videos.append({'url': src, 'poster': poster})
                
            except ImportError:
                print("⚠️ BeautifulSoup 不可用，使用基础解析")
                description = ""
                cleaned_text = page_source
                links = []
                images = []
                videos = []
            
            # 获取页面截图
            screenshot_path = None
            try:
                timestamp = int(time.time())
                screenshot_path = f"enhanced_screenshot_{timestamp}.png"
                self.driver.save_screenshot(screenshot_path)
                print(f"📸 页面截图已保存: {screenshot_path}")
            except Exception as e:
                print(f"⚠️ 截图保存失败: {e}")
            
            result = {
                'url': url,
                'current_url': current_url,
                'title': title,
                'description': description,
                'content_length': len(page_source),
                'text_content': cleaned_text,
                'links': links,
                'images': images,
                'videos': videos,
                'raw_html': page_source,
                'screenshot': screenshot_path,
                'success': True,
                'method': 'enhanced_selenium'
            }
            
            return result
            
        except Exception as e:
            print(f"❌ 数据提取失败: {e}")
            return None
    
    def save_to_file(self, data: Dict[str, Any], filename: str = None) -> str:
        """保存数据到文件"""
        if not filename:
            domain = urlparse(data['url']).netloc
            timestamp = int(time.time())
            filename = f"enhanced_scraped_{domain}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 数据已保存到: {filename}")
            return filename
        except Exception as e:
            print(f"❌ 保存文件失败: {e}")
            return ""
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("🔒 浏览器已关闭")


def main():
    """主函数"""
    print("增强版Selenium网页内容获取工具")
    print("=" * 60)
    
    # 目标URL
    target_url = "https://hsex.men/video-1131562.htm"
    
    # 创建增强版爬虫（使用有头模式，等待60秒）
    scraper = None
    try:
        print("\n🚀 启动增强版Selenium爬虫...")
        scraper = EnhancedSeleniumScraper(headless=False, wait_time=60)
        
        # 爬取内容
        result = scraper.scrape_with_verification(target_url)
        
        if result and result['success']:
            print(f"\n🎉 爬取成功!")
            print(f"🌐 目标URL: {result['url']}")
            print(f"🌐 实际URL: {result['current_url']}")
            print(f"📄 标题: {result['title']}")
            print(f"📝 描述: {result['description']}")
            print(f"🔗 链接数量: {len(result['links'])}")
            print(f"🖼️ 图片数量: {len(result['images'])}")
            print(f"🎬 视频数量: {len(result['videos'])}")
            print(f"📊 内容长度: {result['content_length']} 字符")
            
            # 显示文本预览
            if result['text_content']:
                print(f"\n📖 文本内容预览:")
                print("-" * 40)
                preview = result['text_content'][:500]
                print(preview)
                if len(result['text_content']) > 500:
                    print("... (内容已截断)")
            
            # 显示视频信息
            if result['videos']:
                print(f"\n🎬 视频信息:")
                print("-" * 40)
                for i, video in enumerate(result['videos'], 1):
                    print(f"{i}. 视频URL: {video['url']}")
                    if video['poster']:
                        print(f"   封面: {video['poster']}")
            
            # 保存结果
            filename = scraper.save_to_file(result)
            
            # 显示部分链接
            if result['links']:
                print(f"\n🔗 链接预览 (前5个):")
                print("-" * 40)
                for i, link in enumerate(result['links'][:5], 1):
                    print(f"{i}. {link['text'][:30]}... -> {link['url']}")
            
            if result.get('screenshot'):
                print(f"\n📸 页面截图: {result['screenshot']}")
        
        else:
            print("\n❌ 爬取失败")
            print("可能的原因:")
            print("1. 验证过程需要人工干预")
            print("2. 网站有更严格的反爬虫检测")
            print("3. 网络连接问题")
            print("4. 网站暂时不可用")
    
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
    
    finally:
        if scraper:
            scraper.close()


if __name__ == "__main__":
    main()
