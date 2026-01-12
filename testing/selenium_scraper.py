#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selenium网页内容获取工具
使用真实浏览器模拟来绕过反爬虫保护
"""

import time
import json
import random
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import os


class SeleniumWebScraper:
    """基于Selenium的网页爬虫"""
    
    def __init__(self, headless: bool = True):
        """
        初始化Selenium爬虫
        
        Args:
            headless: 是否使用无头模式（不显示浏览器窗口）
        """
        self.headless = headless
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
            
            # 导入异常类供后续使用
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
            
            # 禁用图片加载以提高速度
            prefs = {
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_setting_values.notifications": 2
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # 创建WebDriver
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # 执行反检测脚本
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✅ Selenium WebDriver 初始化成功")
            
        except ImportError:
            print("❌ 请安装selenium: pip install selenium")
            print("❌ 请安装ChromeDriver: https://chromedriver.chromium.org/")
            raise
        except Exception as e:
            print(f"❌ WebDriver 初始化失败: {e}")
            raise
    
    def _random_delay(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """随机延迟"""
        delay = random.uniform(min_delay, max_delay)
        print(f"等待 {delay:.1f} 秒...")
        time.sleep(delay)
    
    def _simulate_human_behavior(self):
        """模拟人类行为"""
        # 随机滚动
        scroll_height = random.randint(100, 500)
        self.driver.execute_script(f"window.scrollBy(0, {scroll_height});")
        self._random_delay(0.5, 1.5)
        
        # 随机移动鼠标（在无头模式下无效，但保持代码完整性）
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(self.driver)
            actions.move_by_offset(random.randint(10, 100), random.randint(10, 100))
            actions.perform()
        except:
            pass
        
        self._random_delay(1.0, 2.0)
    
    def scrape_url(self, url: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
        """
        使用Selenium爬取网页内容
        
        Args:
            url: 目标URL
            timeout: 超时时间
            
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
            print("⏳ 等待页面加载...")
            self._random_delay(2, 4)
            
            # 模拟人类行为
            self._simulate_human_behavior()
            
            # 等待页面完全加载
            try:
                from selenium.webdriver.support.ui import WebDriverWait
                WebDriverWait(self.driver, timeout).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                print("✅ 页面加载完成")
            except self.TimeoutException:
                print("⚠️ 页面加载超时，继续处理...")
            
            # 检查是否有反爬虫检测
            page_source = self.driver.page_source.lower()
            if any(keyword in page_source for keyword in ['access denied', 'forbidden', 'blocked', 'captcha']):
                print("⚠️ 检测到可能的反爬虫页面")
            
            # 获取页面信息
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
            
            # 使用BeautifulSoup解析（如果可用）
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
                
            except ImportError:
                print("⚠️ BeautifulSoup 不可用，使用基础解析")
                description = ""
                cleaned_text = page_source
                links = []
                images = []
            
            # 获取页面截图（可选）
            screenshot_path = None
            try:
                timestamp = int(time.time())
                screenshot_path = f"screenshot_{timestamp}.png"
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
                'raw_html': page_source,
                'screenshot': screenshot_path,
                'success': True,
                'method': 'selenium'
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
            filename = f"selenium_scraped_{domain}_{timestamp}.json"
        
        try:
            # 移除截图路径中的二进制数据，只保存路径
            save_data = data.copy()
            if 'screenshot' in save_data and save_data['screenshot']:
                # 只保存截图路径，不保存二进制数据
                pass
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
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


def check_dependencies():
    """检查依赖"""
    missing_deps = []
    
    try:
        import selenium
        print(f"✅ Selenium 版本: {selenium.__version__}")
    except ImportError:
        missing_deps.append("selenium")
    
    try:
        from bs4 import BeautifulSoup
        print("✅ BeautifulSoup4 可用")
    except ImportError:
        missing_deps.append("beautifulsoup4")
    
    if missing_deps:
        print(f"❌ 缺少依赖: {', '.join(missing_deps)}")
        print("请运行: pip install " + " ".join(missing_deps))
        return False
    
    return True


def main():
    """主函数"""
    print("Selenium网页内容获取工具")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 目标URL
    target_url = "https://hsex.men/video-1131562.htm"
    
    # 创建爬虫（使用有头模式以便调试）
    scraper = None
    try:
        print("\n🚀 启动Selenium爬虫...")
        scraper = SeleniumWebScraper(headless=False)  # 使用有头模式便于调试
        
        # 爬取内容
        result = scraper.scrape_url(target_url, timeout=30)
        
        if result and result['success']:
            print(f"\n🎉 爬取成功!")
            print(f"🌐 目标URL: {result['url']}")
            print(f"🌐 实际URL: {result['current_url']}")
            print(f"📄 标题: {result['title']}")
            print(f"📝 描述: {result['description']}")
            print(f"🔗 链接数量: {len(result['links'])}")
            print(f"🖼️ 图片数量: {len(result['images'])}")
            print(f"📊 内容长度: {result['content_length']} 字符")
            
            # 显示文本预览
            if result['text_content']:
                print(f"\n📖 文本内容预览:")
                print("-" * 40)
                preview = result['text_content'][:500]
                print(preview)
                if len(result['text_content']) > 500:
                    print("... (内容已截断)")
            
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
            print("1. 网站需要登录")
            print("2. 网站有JavaScript反爬虫检测")
            print("3. 网络连接问题")
            print("4. 网站暂时不可用")
    
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
    
    finally:
        if scraper:
            scraper.close()


if __name__ == "__main__":
    main()
