#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GitHub 项目提取器
从抓取的微信公众号文章中提取所有 GitHub 项目链接，并获取项目描述
"""

import re
import json
import time
import requests
from pathlib import Path
from typing import List, Dict, Set, Optional
from collections import defaultdict
from loguru import logger


class GitHubExtractor:
    """GitHub 项目链接提取器"""
    
    def __init__(self, articles_dir: str = "./articles", github_token: Optional[str] = None):
        self.articles_dir = Path(articles_dir)
        self.github_pattern = re.compile(
            r'https?://github\.com/([a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+)',
            re.IGNORECASE
        )
        self.github_token = github_token
        self.session = requests.Session()
        if github_token:
            self.session.headers.update({'Authorization': f'token {github_token}'})
        self.repo_cache = {}  # 缓存已查询的仓库信息
        
    def extract_from_file(self, file_path: Path) -> List[Dict[str, str]]:
        """从单个文件中提取 GitHub 链接及其上下文"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找所有 GitHub 链接及其上下文
            repos_info = []
            
            # 按行处理，提取上下文
            lines = content.split('\n')
            for i, line in enumerate(lines):
                matches = self.github_pattern.finditer(line)
                
                for match in matches:
                    repo_path = match.group(1)
                    
                    # 清理仓库路径
                    repo = repo_path.split('/blob/')[0]
                    repo = repo.split('/tree/')[0]
                    repo = repo.split('#')[0]
                    repo = repo.strip('/')
                    
                    url = f"https://github.com/{repo}"
                    
                    # 提取上下文（当前行及前后各1行）
                    context_lines = []
                    for j in range(max(0, i-1), min(len(lines), i+2)):
                        context_lines.append(lines[j].strip())
                    context = ' '.join(context_lines)
                    
                    # 清理上下文中的 Markdown 语法
                    context = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', context)
                    context = re.sub(r'[#*`]', '', context)
                    context = context.strip()
                    
                    repos_info.append({
                        'url': url,
                        'repo': repo,
                        'context': context[:200]  # 限制上下文长度
                    })
            
            return repos_info
            
        except Exception as e:
            logger.error(f"读取文件失败 {file_path}: {e}")
            return []
    
    def get_repo_info_from_github(self, repo_path: str) -> Optional[Dict]:
        """从 GitHub API 获取仓库信息"""
        
        # 检查缓存
        if repo_path in self.repo_cache:
            return self.repo_cache[repo_path]
        
        try:
            api_url = f"https://api.github.com/repos/{repo_path}"
            response = self.session.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                info = {
                    'name': data.get('name', ''),
                    'full_name': data.get('full_name', ''),
                    'description': data.get('description', ''),
                    'stars': data.get('stargazers_count', 0),
                    'language': data.get('language', ''),
                    'topics': data.get('topics', []),
                    'homepage': data.get('homepage', ''),
                    'created_at': data.get('created_at', ''),
                    'updated_at': data.get('updated_at', '')
                }
                self.repo_cache[repo_path] = info
                return info
            elif response.status_code == 404:
                logger.warning(f"仓库不存在: {repo_path}")
                return None
            elif response.status_code == 403:
                logger.warning(f"API 限流，跳过: {repo_path}")
                return None
            else:
                logger.error(f"获取仓库信息失败: {repo_path}, 状态码: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"请求 GitHub API 失败 {repo_path}: {e}")
            return None
    
    def extract_all(self, fetch_github_info: bool = False) -> Dict:
        """提取所有文章中的 GitHub 链接"""
        
        if not self.articles_dir.exists():
            logger.error(f"文章目录不存在: {self.articles_dir}")
            return {}
        
        # 存储所有找到的仓库（URL -> 详细信息）
        all_repos_dict = {}
        
        # 遍历所有 Markdown 文件
        markdown_files = list(self.articles_dir.rglob("*.md"))
        
        if not markdown_files:
            logger.warning("未找到任何 Markdown 文件")
            return {}
        
        logger.info(f"开始扫描 {len(markdown_files)} 个文件...")
        
        # 第一步：提取所有链接和上下文
        for file_path in markdown_files:
            repos_info = self.extract_from_file(file_path)
            
            if repos_info:
                source = file_path.parent.name
                article_title = file_path.stem
                
                for repo_info in repos_info:
                    url = repo_info['url']
                    repo = repo_info['repo']
                    context = repo_info['context']
                    
                    if url not in all_repos_dict:
                        all_repos_dict[url] = {
                            'url': url,
                            'repo': repo,
                            'description': '',
                            'context_from_articles': [],
                            'mentioned_in': [],
                            'stars': 0,
                            'language': '',
                            'topics': []
                        }
                    
                    # 添加上下文和来源
                    if context and context not in all_repos_dict[url]['context_from_articles']:
                        all_repos_dict[url]['context_from_articles'].append(context)
                    
                    all_repos_dict[url]['mentioned_in'].append({
                        'source': source,
                        'article': article_title
                    })
                
                logger.info(f"✓ {article_title}: 发现 {len(repos_info)} 个 GitHub 项目")
        
        logger.info(f"共发现 {len(all_repos_dict)} 个不同的 GitHub 项目")
        
        # 第二步：从 GitHub API 获取项目描述（可选）
        if fetch_github_info:
            logger.info("正在从 GitHub API 获取项目信息...")
            total = len(all_repos_dict)
            
            for idx, (url, repo_data) in enumerate(all_repos_dict.items(), 1):
                repo_path = repo_data['repo']
                logger.info(f"[{idx}/{total}] 获取: {repo_path}")
                
                github_info = self.get_repo_info_from_github(repo_path)
                
                if github_info:
                    repo_data['description'] = github_info.get('description', '')
                    repo_data['stars'] = github_info.get('stars', 0)
                    repo_data['language'] = github_info.get('language', '')
                    repo_data['topics'] = github_info.get('topics', [])
                    repo_data['homepage'] = github_info.get('homepage', '')
                
                # 避免请求过快
                if idx % 10 == 0:
                    time.sleep(1)
        
        # 转换为列表并排序
        all_repos_list = sorted(all_repos_dict.values(), key=lambda x: x['url'])
        
        return {
            'total_count': len(all_repos_list),
            'repositories': all_repos_list
        }
    
    def save_results(self, results: Dict, output_file: str = "github_repos.json"):
        """保存结果到文件"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logger.success(f"结果已保存到: {output_file}")
        except Exception as e:
            logger.error(f"保存失败: {e}")
    
    def print_summary(self, results: Dict):
        """打印统计摘要"""
        print("\n" + "=" * 80)
        print("📊 GitHub 项目提取结果")
        print("=" * 80)
        
        if not results.get('repositories'):
            print("未找到任何 GitHub 项目")
            return
        
        repos = results['repositories']
        total = results['total_count']
        
        # 总体统计
        print(f"\n【总体统计】")
        print(f"  GitHub 项目总数: {total}")
        
        # 按热度排序（按提及次数）
        repos_by_mentions = sorted(repos, key=lambda x: len(x['mentioned_in']), reverse=True)
        
        print(f"\n【热门项目 TOP 10】(按提及次数)")
        for idx, repo in enumerate(repos_by_mentions[:10], 1):
            mentions = len(repo['mentioned_in'])
            desc = repo['description'][:60] if repo['description'] else "无描述"
            print(f"  {idx}. {repo['url']}")
            print(f"     提及次数: {mentions}, 描述: {desc}...")
        
        print(f"\n【完整项目列表】({total} 个)")
        print("  详见输出文件: github_repos_full.md 或 github_repos_full.json")
        print("=" * 80)
    
    def export_to_markdown(self, results: Dict, output_file: str = "github_repos_full.md"):
        """导出为 Markdown 格式（完整列表）"""
        try:
            repos = results.get('repositories', [])
            total = results.get('total_count', 0)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("# GitHub 项目完整列表\n\n")
                f.write(f"> 共收录 **{total}** 个 GitHub 项目\n\n")
                f.write("---\n\n")
                
                # 目录
                f.write("## 📑 目录\n\n")
                f.write("- [完整列表（按字母顺序）](#完整列表)\n")
                f.write("- [热门项目（按提及次数）](#热门项目)\n")
                f.write("- [按星标排序](#按星标排序)\n\n")
                f.write("---\n\n")
                
                # 完整列表（按字母顺序）
                f.write("## 📋 完整列表\n\n")
                f.write("> 所有项目按字母顺序排列\n\n")
                
                for idx, repo in enumerate(sorted(repos, key=lambda x: x['url']), 1):
                    f.write(f"### {idx}. {repo['repo']}\n\n")
                    f.write(f"**URL**: [{repo['url']}]({repo['url']})\n\n")
                    
                    # 描述
                    if repo['description']:
                        f.write(f"**描述**: {repo['description']}\n\n")
                    elif repo['context_from_articles']:
                        f.write(f"**文章中的介绍**: {repo['context_from_articles'][0]}\n\n")
                    else:
                        f.write(f"**描述**: 暂无描述\n\n")
                    
                    # 其他信息
                    if repo.get('stars'):
                        f.write(f"**⭐ Stars**: {repo['stars']:,}  \n")
                    if repo.get('language'):
                        f.write(f"**💻 Language**: {repo['language']}  \n")
                    if repo.get('topics'):
                        topics_str = ', '.join(f"`{t}`" for t in repo['topics'][:5])
                        f.write(f"**🏷️ Topics**: {topics_str}  \n")
                    
                    # 提及信息
                    mentions = len(repo['mentioned_in'])
                    f.write(f"**📊 提及次数**: {mentions}  \n")
                    
                    # 来源文章
                    sources = list(set(m['source'] for m in repo['mentioned_in']))
                    f.write(f"**📚 来源公众号**: {', '.join(sources)}\n\n")
                    
                    f.write("---\n\n")
                
                # 热门项目
                f.write("## 🔥 热门项目\n\n")
                f.write("> 按提及次数排序\n\n")
                
                hot_repos = sorted(repos, key=lambda x: len(x['mentioned_in']), reverse=True)
                for idx, repo in enumerate(hot_repos[:20], 1):
                    mentions = len(repo['mentioned_in'])
                    desc = repo['description'][:100] if repo['description'] else "暂无描述"
                    f.write(f"{idx}. **[{repo['repo']}]({repo['url']})** (提及 {mentions} 次)\n")
                    f.write(f"   {desc}\n\n")
                
                # 按星标排序
                starred_repos = [r for r in repos if r.get('stars', 0) > 0]
                if starred_repos:
                    f.write("## ⭐ 按星标排序\n\n")
                    f.write("> 按 GitHub Stars 数量排序\n\n")
                    
                    starred_repos_sorted = sorted(starred_repos, key=lambda x: x['stars'], reverse=True)
                    for idx, repo in enumerate(starred_repos_sorted[:20], 1):
                        stars = repo['stars']
                        desc = repo['description'][:100] if repo['description'] else "暂无描述"
                        f.write(f"{idx}. **[{repo['repo']}]({repo['url']})** ({stars:,} ⭐)\n")
                        f.write(f"   {desc}\n\n")
            
            logger.success(f"Markdown 完整列表已保存到: {output_file}")
            
        except Exception as e:
            logger.error(f"导出 Markdown 失败: {e}")
    
    def export_to_txt(self, results: Dict, output_file: str = "github_repos_full.txt"):
        """导出为纯文本（URL + 描述）"""
        try:
            repos = results.get('repositories', [])
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"GitHub 项目列表 (共 {len(repos)} 个)\n")
                f.write("=" * 80 + "\n\n")
                
                for idx, repo in enumerate(sorted(repos, key=lambda x: x['url']), 1):
                    f.write(f"{idx}. {repo['url']}\n")
                    
                    desc = repo['description'] if repo['description'] else \
                           (repo['context_from_articles'][0] if repo['context_from_articles'] else "暂无描述")
                    
                    f.write(f"   描述: {desc}\n")
                    
                    if repo.get('stars'):
                        f.write(f"   Stars: {repo['stars']:,}\n")
                    
                    mentions = len(repo['mentioned_in'])
                    f.write(f"   提及: {mentions} 次\n")
                    f.write("\n")
            
            logger.success(f"TXT 列表已保存到: {output_file}")
        except Exception as e:
            logger.error(f"导出 TXT 失败: {e}")


def main():
    """主函数"""
    import sys
    import os
    
    print("=" * 80)
    print("GitHub 项目提取器 - 完整列表版本")
    print("=" * 80)
    
    # 检查文章目录
    articles_dir = "./articles"
    if not Path(articles_dir).exists():
        print(f"\n❌ 错误: 文章目录不存在: {articles_dir}")
        print("提示: 请先运行 main.py 抓取文章")
        return
    
    # 检查是否获取 GitHub 信息
    print("\n是否从 GitHub API 获取项目详细信息？")
    print("  - 输入 'y': 获取（需要较长时间，会获取 Stars、语言等信息）")
    print("  - 输入 'n': 不获取（仅提取文章中的信息，速度快）")
    
    fetch_info = input("\n请选择 (y/n，默认 n): ").strip().lower() == 'y'
    
    # GitHub Token（可选）
    github_token = os.getenv('GITHUB_TOKEN')
    if fetch_info and not github_token:
        print("\n提示: 未设置 GITHUB_TOKEN 环境变量")
        print("  - 未认证的请求限制为 60次/小时")
        print("  - 认证请求限制为 5000次/小时")
        print("  - 可通过设置环境变量提高限制: export GITHUB_TOKEN=your_token")
    
    # 创建提取器
    extractor = GitHubExtractor(articles_dir, github_token=github_token)
    
    print(f"\n正在扫描文章目录: {articles_dir}")
    print("这可能需要一些时间...\n")
    
    # 提取链接
    results = extractor.extract_all(fetch_github_info=fetch_info)
    
    if not results.get('repositories'):
        print("\n❌ 未找到任何 GitHub 项目")
        return
    
    # 打印摘要
    extractor.print_summary(results)
    
    # 保存结果
    print("\n正在保存结果...")
    extractor.save_results(results, "github_repos_full.json")
    extractor.export_to_markdown(results, "github_repos_full.md")
    extractor.export_to_txt(results, "github_repos_full.txt")
    
    print("\n✅ 完成！生成了以下文件:")
    print("  - github_repos_full.json  (JSON 格式，包含所有详细信息)")
    print("  - github_repos_full.md    (Markdown 格式，完整项目列表)")
    print("  - github_repos_full.txt   (纯文本格式，URL + 描述)")
    print("\n💡 提示: 可以直接查看 github_repos_full.md 文件获取完整列表")
    print("=" * 80)


if __name__ == "__main__":
    main()
