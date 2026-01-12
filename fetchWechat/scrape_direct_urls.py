#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
直接抓取微信文章 URL
适用于：您已经有真实的 mp.weixin.qq.com URL 列表

用法:
    python scrape_direct_urls.py urls.txt
    
urls.txt 格式（每行一个URL）:
    https://mp.weixin.qq.com/s/xxx
    https://mp.weixin.qq.com/s/yyy
"""

import sys
from pathlib import Path
from scraper import WeChatScraper
from loguru import logger

def scrape_from_file(url_file: str, account_name: str = "直接抓取"):
    """
    从文件中读取 URL 列表并抓取
    
    Args:
        url_file: URL 文件路径
        account_name: 公众号名称（用于分类）
    """
    url_path = Path(url_file)
    
    if not url_path.exists():
        logger.error(f"文件不存在: {url_file}")
        return
    
    # 读取 URL 列表
    with open(url_path, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip() and line.strip().startswith('http')]
    
    logger.info(f"从 {url_file} 读取到 {len(urls)} 个 URL")
    
    if not urls:
        logger.warning("没有找到有效的 URL")
        return
    
    # 创建采集器
    scraper = WeChatScraper()
    
    success_count = 0
    fail_count = 0
    
    for idx, url in enumerate(urls, 1):
        logger.info(f"\n[{idx}/{len(urls)}] 正在抓取: {url[:80]}...")
        
        try:
            # 抓取文章
            result = scraper.scrape_article(url)
            
            if not result or (not result['markdown'] and not result['html']):
                logger.error(f"  ❌ 抓取失败或内容为空")
                fail_count += 1
                continue
            
            # 检查内容长度
            content = result['markdown'] if result['markdown'] else result['html']
            if len(content) < 200:
                logger.warning(f"  ⚠️ 内容过短 ({len(content)} 字符)，可能不是真实文章")
                fail_count += 1
                continue
            
            # 保存
            title = result['metadata'].get('title', f'untitled_{idx}')
            scraper.save_markdown(
                content=content,
                title=title,
                source=account_name,
                metadata={
                    'title': title,
                    'url': url,
                    'source': account_name
                }
            )
            
            success_count += 1
            logger.success(f"  ✅ 成功! ({len(content)} 字符)")
            
        except Exception as e:
            logger.error(f"  ❌ 异常: {e}")
            fail_count += 1
    
    logger.info("\n" + "="*60)
    logger.success(f"抓取完成!")
    logger.info(f"  ✅ 成功: {success_count} 篇")
    logger.info(f"  ❌ 失败: {fail_count} 篇")
    logger.info("="*60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    url_file = sys.argv[1]
    account_name = sys.argv[2] if len(sys.argv) > 2 else "直接抓取"
    
    scrape_from_file(url_file, account_name)
