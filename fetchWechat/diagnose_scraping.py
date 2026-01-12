#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
诊断 Selenium 抓取问题
检查为什么一页只抓取 1 条
"""

import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def diagnose_scraping(account_name: str):
    """诊断抓取问题"""
    
    print(f"\n{'='*60}")
    print(f"诊断抓取问题: {account_name}")
    print(f"{'='*60}\n")
    
    # 初始化浏览器
    options = ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # 访问搜索页
        url = f"https://weixin.sogou.com/weixin?type=2&query={account_name}&page=1"
        print(f"访问: {url}\n")
        
        driver.get(url)
        time.sleep(5)
        
        # 检查是否有验证码
        if "antispider" in driver.current_url:
            print("❌ 触发验证码！")
            print("   请在浏览器中手动完成验证...")
            input("   完成后按 Enter 继续: ")
        
        # 解析页面
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        news_list = soup.find_all('div', class_='news-box')
        
        print(f"✅ 找到 {len(news_list)} 个新闻条目\n")
        
        if not news_list:
            print("❌ 没有找到新闻条目！")
            print("   可能原因:")
            print("   1. 页面结构变化")
            print("   2. 搜索结果为空")
            print("   3. 反爬虫拦截")
            return
        
        # 逐个分析
        for i, news in enumerate(news_list[:5], 1):  # 只测试前 5 个
            print(f"\n{'─'*60}")
            print(f"条目 {i}:")
            print(f"{'─'*60}")
            
            # 标题
            title_elem = news.find('h3')
            if not title_elem:
                print("  ❌ 没有找到标题元素")
                continue
            
            link_elem = title_elem.find('a')
            if not link_elem:
                print("  ❌ 没有找到链接元素")
                continue
            
            title = link_elem.text.strip()
            sogou_url = link_elem.get('href', '')
            
            if sogou_url.startswith('/'):
                sogou_url = "https://weixin.sogou.com" + sogou_url
            
            print(f"  标题: {title[:50]}...")
            print(f"  搜狗URL: {sogou_url[:80]}...")
            
            # 尝试跟踪重定向
            print(f"  尝试跟踪重定向...")
            
            try:
                # 打开新标签页
                original_window = driver.current_window_handle
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
                
                driver.get(sogou_url)
                time.sleep(3)
                
                final_url = driver.current_url
                
                # 关闭新标签页
                driver.close()
                driver.switch_to.window(original_window)
                
                if 'mp.weixin.qq.com' in final_url:
                    print(f"  ✅ 成功! 真实URL: {final_url[:80]}...")
                elif 'antispider' in final_url:
                    print(f"  ❌ 触发验证码: {final_url[:80]}...")
                    print(f"  → 这就是为什么只抓取 1 条的原因！")
                    
                    # 询问是否继续
                    answer = input("\n是否手动完成验证码并继续测试? (y/n): ")
                    if answer.lower() != 'y':
                        break
                else:
                    print(f"  ⚠️  未跳转到微信: {final_url[:80]}...")
                
            except Exception as e:
                print(f"  ❌ 跟踪失败: {e}")
                # 确保返回原窗口
                try:
                    if len(driver.window_handles) > 1:
                        driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                except:
                    pass
        
        print(f"\n{'='*60}")
        print("诊断总结")
        print(f"{'='*60}")
        print(f"\n找到 {len(news_list)} 个条目")
        print(f"\n常见问题:")
        print(f"1. 跟踪重定向触发验证码 → 导致大部分条目跳过")
        print(f"2. 频繁请求触发反爬虫 → 成功率很低")
        print(f"3. 需要手动处理验证码 → 影响自动化")
        
        print(f"\n解决方案:")
        print(f"1. 增加延迟时间（当前测试已增加到 3 秒）")
        print(f"2. 减少抓取数量（每次 5-10 条）")
        print(f"3. 使用 RSSHub 方案（避免搜狗）")
        print(f"4. 分批次抓取（间隔 5-10 分钟）")
        
    finally:
        driver.quit()
        print(f"\n浏览器已关闭")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python diagnose_scraping.py '公众号名称'")
        print("\n示例:")
        print("  python diagnose_scraping.py '逛逛GitHub'")
        sys.exit(1)
    
    account_name = sys.argv[1]
    diagnose_scraping(account_name)
