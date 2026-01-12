#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloudflare绕过工具
专门用于绕过Cloudflare保护并获取真实页面内容
"""

import time
import json
import random
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import os


class CloudflareBypass:
    """Cloudflare绕过工具"""
    
    def __init__(self, headless: bool = False, max_wait: int = 120):
        """
        初始化Cloudflare绕过工具
        
        Args:
            headless: 是否使用无头模式
            max_wait: 最大等待时间（秒）
        """
        self.headless = headless
        self.max_wait = max_wait
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
            from selenium.webdriver.common.action_chains import ActionChains
            from selenium.common.exceptions import TimeoutException, WebDriverException
            
            # 导入异常类
            self.TimeoutException = TimeoutException
            self.WebDriverException = WebDriverException
            self.By = By
            self.EC = EC
            self.ActionChains = ActionChains
            
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
            
            # 启用所有功能
            prefs = {
                "profile.managed_default_content_settings.images": 1,
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.media_stream": 1,
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # 创建WebDriver
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # 执行反检测脚本
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
            
            print("✅ Cloudflare绕过工具初始化成功")
            
        except ImportError:
            print("❌ 请安装selenium: pip install selenium")
            raise
        except Exception as e:
            print(f"❌ WebDriver 初始化失败: {e}")
            raise
    
    def _human_like_delay(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """人类化延迟"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _simulate_human_behavior(self):
        """模拟人类行为"""
        try:
            # 随机滚动
            for _ in range(random.randint(2, 5)):
                scroll_height = random.randint(100, 500)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_height});")
                self._human_like_delay(0.5, 1.5)
            
            # 随机移动鼠标
            actions = self.ActionChains(self.driver)
            for _ in range(random.randint(3, 7)):
                x_offset = random.randint(-100, 100)
                y_offset = random.randint(-100, 100)
                actions.move_by_offset(x_offset, y_offset)
                actions.perform()
                self._human_like_delay(0.3, 0.8)
            
            # 随机点击（在安全区域）
            try:
                body = self.driver.find_element(self.By.TAG_NAME, "body")
                actions = self.ActionChains(self.driver)
                actions.move_to_element_with_offset(body, random.randint(50, 200), random.randint(50, 200))
                actions.click()
                actions.perform()
            except:
                pass
            
        except Exception as e:
            print(f"⚠️ 模拟人类行为时出错: {e}")
    
    def _wait_for_cloudflare_bypass(self, timeout: int = 120) -> bool:
        """等待Cloudflare验证完成"""
        print(f"⏳ 等待Cloudflare验证完成（最多{timeout}秒）...")
        
        start_time = time.time()
        last_title = ""
        last_url = ""
        verification_attempts = 0
        
        while time.time() - start_time < timeout:
            try:
                current_title = self.driver.title
                current_url = self.driver.current_url
                page_source = self.driver.page_source.lower()
                
                # 检查是否还在验证页面
                is_verification_page = any(keyword in page_source for keyword in [
                    'cloudflare', 'challenge', 'verification', '验证', '请稍候', 'checking your browser'
                ])
                
                # 检查是否有验证成功标识
                verification_success = any(keyword in page_source for keyword in [
                    'verification successful', '验证成功', 'challenge-success'
                ])
                
                # 检查标题和URL变化
                title_changed = current_title != last_title and current_title not in ["请稍候…", "Just a moment...", "Checking your browser..."]
                url_changed = current_url != last_url
                
                # 检查是否跳转到实际内容页面
                if not is_verification_page and (title_changed or url_changed or verification_success):
                    print(f"✅ 检测到页面变化:")
                    print(f"   标题: {current_title}")
                    print(f"   URL: {current_url}")
                    return True
                
                # 检查是否有验证按钮需要点击
                try:
                    # 查找可能的验证按钮
                    verify_buttons = self.driver.find_elements(self.By.CSS_SELECTOR, 
                        "input[type='submit'], button, .ctp-button, [class*='verify'], [class*='challenge']")
                    
                    for button in verify_buttons:
                        if button.is_displayed() and button.is_enabled():
                            print(f"🖱️ 发现验证按钮，尝试点击...")
                            self.driver.execute_script("arguments[0].click();", button)
                            verification_attempts += 1
                            self._human_like_delay(2, 4)
                            break
                except:
                    pass
                
                # 检查Turnstile验证框
                try:
                    turnstile_frame = self.driver.find_element(self.By.CSS_SELECTOR, "iframe[src*='turnstile']")
                    if turnstile_frame.is_displayed():
                        print("🔄 检测到Turnstile验证框，等待自动完成...")
                        self._human_like_delay(5, 10)
                except:
                    pass
                
                # 模拟人类行为
                if verification_attempts < 3:  # 限制验证尝试次数
                    self._simulate_human_behavior()
                
                last_title = current_title
                last_url = current_url
                
                # 每10秒报告一次状态
                elapsed = int(time.time() - start_time)
                if elapsed % 10 == 0 and elapsed > 0:
                    print(f"⏰ 已等待 {elapsed} 秒，当前状态: {current_title}")
                
                time.sleep(2)
                
            except Exception as e:
                print(f"⚠️ 检查验证状态时出错: {e}")
                time.sleep(2)
        
        print(f"⏰ 等待超时（{timeout}秒）")
        return False
    
    def bypass_cloudflare(self, url: str) -> Optional[Dict[str, Any]]:
        """
        绕过Cloudflare并获取真实内容
        
        Args:
            url: 目标URL
            
        Returns:
            包含真实页面信息的字典
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
            self._human_like_delay(3, 5)
            
            # 模拟人类行为
            self._simulate_human_behavior()
            
            # 检查是否是Cloudflare验证页面
            page_source = self.driver.page_source.lower()
            if any(keyword in page_source for keyword in ['cloudflare', 'challenge', 'verification', '验证']):
                print("🛡️ 检测到Cloudflare验证页面，开始绕过...")
                
                # 等待验证完成
                bypass_success = self._wait_for_cloudflare_bypass(self.max_wait)
                
                if bypass_success:
                    print("✅ Cloudflare验证绕过成功！")
                    self._human_like_delay(3, 5)  # 等待页面完全加载
                else:
                    print("⚠️ Cloudflare验证未完成，获取当前内容")
            else:
                print("✅ 无需Cloudflare验证")
            
            # 获取最终页面信息
            result = self._extract_real_content(url)
            
            if result:
                print("✅ 真实内容提取成功")
                return result
            else:
                print("❌ 内容提取失败")
                return None
                
        except self.WebDriverException as e:
            print(f"❌ WebDriver 错误: {e}")
            return None
        except Exception as e:
            print(f"❌ 绕过过程中发生错误: {e}")
            return None
    
    def _extract_real_content(self, url: str) -> Optional[Dict[str, Any]]:
        """提取真实页面内容"""
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
                
                # 查找视频源
                video_sources = []
                for source in soup.find_all('source'):
                    src = source.get('src')
                    if src and any(ext in src.lower() for ext in ['.mp4', '.webm', '.ogg', '.avi', '.mov']):
                        if src.startswith('/'):
                            src = f"{urlparse(url).scheme}://{urlparse(url).netloc}{src}"
                        elif not src.startswith(('http://', 'https://')):
                            src = f"{urlparse(url).scheme}://{urlparse(url).netloc}/{src}"
                        video_sources.append({'url': src, 'type': source.get('type', '')})
                
            except ImportError:
                print("⚠️ BeautifulSoup 不可用，使用基础解析")
                description = ""
                cleaned_text = page_source
                links = []
                images = []
                videos = []
                video_sources = []
            
            # 获取页面截图
            screenshot_path = None
            try:
                timestamp = int(time.time())
                screenshot_path = f"real_content_screenshot_{timestamp}.png"
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
                'video_sources': video_sources,
                'raw_html': page_source,
                'screenshot': screenshot_path,
                'success': True,
                'method': 'cloudflare_bypass',
                'is_real_content': not any(keyword in page_source.lower() for keyword in ['cloudflare', 'challenge', 'verification', '验证'])
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
            filename = f"real_content_{domain}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 真实内容已保存到: {filename}")
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
    print("Cloudflare绕过工具")
    print("=" * 60)
    
    # 目标URL
    target_url = "https://hsex.men/video-1131562.htm"
    
    # 创建绕过工具（使用有头模式，等待120秒）
    bypass_tool = None
    try:
        print("\n🚀 启动Cloudflare绕过工具...")
        bypass_tool = CloudflareBypass(headless=False, max_wait=120)
        
        # 绕过Cloudflare并获取真实内容
        result = bypass_tool.bypass_cloudflare(target_url)
        
        if result and result['success']:
            print(f"\n🎉 获取真实内容成功!")
            print(f"🌐 目标URL: {result['url']}")
            print(f"🌐 实际URL: {result['current_url']}")
            print(f"📄 标题: {result['title']}")
            print(f"📝 描述: {result['description']}")
            print(f"🔗 链接数量: {len(result['links'])}")
            print(f"🖼️ 图片数量: {len(result['images'])}")
            print(f"🎬 视频数量: {len(result['videos'])}")
            print(f"🎥 视频源数量: {len(result['video_sources'])}")
            print(f"📊 内容长度: {result['content_length']} 字符")
            print(f"✅ 是否为真实内容: {result['is_real_content']}")
            
            # 显示文本预览
            if result['text_content']:
                print(f"\n📖 文本内容预览:")
                print("-" * 40)
                preview = result['text_content'][:1000]
                print(preview)
                if len(result['text_content']) > 1000:
                    print("... (内容已截断)")
            
            # 显示视频信息
            if result['videos']:
                print(f"\n🎬 视频元素:")
                print("-" * 40)
                for i, video in enumerate(result['videos'], 1):
                    print(f"{i}. 视频URL: {video['url']}")
                    if video['poster']:
                        print(f"   封面: {video['poster']}")
            
            if result['video_sources']:
                print(f"\n🎥 视频源:")
                print("-" * 40)
                for i, source in enumerate(result['video_sources'], 1):
                    print(f"{i}. 源URL: {source['url']}")
                    print(f"   类型: {source['type']}")
            
            # 保存结果
            filename = bypass_tool.save_to_file(result)
            
            # 显示部分链接
            if result['links']:
                print(f"\n🔗 链接预览 (前10个):")
                print("-" * 40)
                for i, link in enumerate(result['links'][:10], 1):
                    print(f"{i}. {link['text'][:50]}... -> {link['url']}")
            
            if result.get('screenshot'):
                print(f"\n📸 页面截图: {result['screenshot']}")
        
        else:
            print("\n❌ 获取真实内容失败")
            print("可能的原因:")
            print("1. Cloudflare验证需要人工干预")
            print("2. 网站有更严格的反爬虫检测")
            print("3. 网络连接问题")
            print("4. 网站暂时不可用")
    
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
    
    finally:
        if bypass_tool:
            bypass_tool.close()


if __name__ == "__main__":
    main()
