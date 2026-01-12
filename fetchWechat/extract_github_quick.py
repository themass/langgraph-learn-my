#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速提取 GitHub 项目（非交互模式）
"""

import sys
import os

# 设置为非交互模式
os.environ['GITHUB_EXTRACT_AUTO'] = '1'

# 导入并运行
sys.path.insert(0, os.path.dirname(__file__))

from extract_github import GitHubExtractor
from pathlib import Path

def quick_extract():
    """快速提取（不调用 GitHub API）"""
    
    print("\n" + "="*60)
    print("GitHub 项目快速提取")
    print("="*60 + "\n")
    
    articles_dir = Path("./articles")
    
    if not articles_dir.exists():
        print("❌ articles 目录不存在")
        print("   请先运行抓取脚本下载文章")
        return
    
    print(f"📂 扫描目录: {articles_dir.absolute()}\n")
    
    extractor = GitHubExtractor(str(articles_dir))
    
    # 快速提取（不调用 GitHub API）
    results = extractor.extract_all(fetch_github_info=False)
    
    if results['total_count'] == 0:
        print("⚠️  没有找到 GitHub 项目")
        return
    
    # 保存结果
    print(f"\n保存结果...")
    extractor.save_results(results, "github_projects_quick.json")
    extractor.export_to_markdown(results, "github_projects_quick.md")
    extractor.export_to_txt(results, "github_projects_quick.txt")
    
    print(f"\n" + "="*60)
    print(f"✅ 完成!")
    print(f"="*60)
    print(f"\n📊 统计:")
    print(f"  - 总项目数: {results['total_count']}")
    print(f"\n📁 文件:")
    print(f"  - github_projects_quick.json")
    print(f"  - github_projects_quick.md")
    print(f"  - github_projects_quick.txt")
    print(f"\n💡 查看报告: cat github_projects_quick.md | head -100")
    print("="*60 + "\n")


if __name__ == "__main__":
    quick_extract()
