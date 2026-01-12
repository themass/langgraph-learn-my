#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查搜狗页面结构
诊断为什么只找到 1 个条目
"""

import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def check_page_structure(account_name: str):
    """检查页面结构"""
    
    print(f"\n{'='*60}")
    print(f"检查搜狗页面结构: {account_name}")
    print(f"{'='*60}\n")
    
    # 初始化浏览器
    options = ChromeOptions()
    # 不使用无头模式，可以看到页面
    # options.add_argument('--headless')
    
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # 访问搜索页
        url = f"https://weixin.sogou.com/weixin?type=2&query={account_name}&page=1"
        print(f"访问: {url}\n")
        
        driver.get(url)
        time.sleep(5)
        
        # 保存页面源码
        with open('page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("✅ 页面源码已保存到 page_source.html\n")
        
        # 尝试不同的 CSS 选择器
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        print("尝试不同的选择器:")
        print("-" * 60)
        
        # 选择器 1: news-box
        news_box = soup.find_all('div', class_='news-box')
        print(f"1. div.news-box: 找到 {len(news_box)} 个")
        
        # 选择器 2: news-list
        news_list = soup.find_all('ul', class_='news-list')
        print(f"2. ul.news-list: 找到 {len(news_list)} 个")
        if news_list:
            items = news_list[0].find_all('li')
            print(f"   └─ li 子元素: {len(items)} 个")
        
        # 选择器 3: txt-box
        txt_box = soup.find_all('div', class_='txt-box')
        print(f"3. div.txt-box: 找到 {len(txt_box)} 个")
        
        # 选择器 4: 所有包含 h3 的 div
        divs_with_h3 = soup.find_all('div', recursive=True)
        divs_containing_h3 = [div for div in divs_with_h3 if div.find('h3')]
        print(f"4. 包含 h3 的 div: 找到 {len(divs_containing_h3)} 个")
        
        # 选择器 5: 直接找所有 h3
        all_h3 = soup.find_all('h3')
        print(f"5. 所有 h3 标签: 找到 {len(all_h3)} 个")
        
        print("\n" + "=" * 60)
        print("详细分析:")
        print("=" * 60)
        
        if all_h3:
            print(f"\n找到 {len(all_h3)} 个标题:")
            for i, h3 in enumerate(all_h3[:5], 1):  # 只显示前 5 个
                title = h3.text.strip()
                parent = h3.parent
                print(f"\n{i}. 标题: {title[:50]}...")
                print(f"   父元素: {parent.name if parent else 'None'}")
                print(f"   父元素 class: {parent.get('class') if parent else 'None'}")
                
                # 查找链接
                link = h3.find('a')
                if link:
                    print(f"   链接: {link.get('href', 'None')[:80]}...")
        
        print("\n" + "=" * 60)
        print("建议:")
        print("=" * 60)
        
        if len(all_h3) >= 10:
            print("✅ 页面有 10+ 个标题，可能是选择器问题")
            print("   建议: 修改代码，使用正确的选择器")
        elif len(all_h3) == 1:
            print("❌ 页面只有 1 个标题")
            print("   可能原因:")
            print("   1. 搜狗返回的是单条文章页")
            print("   2. 触发了反爬虫，页面内容被限制")
            print("   3. 公众号文章太少")
        else:
            print("⚠️  页面有少量标题")
            print("   需要人工查看 page_source.html 确认")
        
        print("\n请手动检查浏览器窗口，看看实际显示了什么")
        input("查看完毕后按 Enter 继续...")
        
    finally:
        driver.quit()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        account_name = "逛逛GitHub"
        print(f"使用默认公众号: {account_name}")
    else:
        account_name = sys.argv[1]
    
    check_page_structure(account_name)
