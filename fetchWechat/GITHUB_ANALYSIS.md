# GitHub 项目分析指南

## 🎯 目标

从已下载的微信文章中提取并分析所有 GitHub 项目。

---

## 🚀 快速开始

### 方法 1: 基础提取（最简单）

```bash
cd fetchWechat
python extract_github.py
```

**输出**：
- `github_projects.json` - JSON 格式
- `github_projects.md` - Markdown 报告
- `github_projects.txt` - 纯文本列表

---

### 方法 2: 带 GitHub API（推荐）

获取更详细的信息（Stars、语言、Topics等）

```bash
# 1. 设置 GitHub Token（可选，但推荐）
export GITHUB_TOKEN=ghp_your_token_here

# 2. 运行提取
python extract_github.py

# 如果没有 token，会提示但仍可运行（无详细信息）
```

**如何获取 GitHub Token**：
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 勾选 `public_repo` 权限
4. 生成并复制 token

---

## 📊 输出示例

### JSON 格式 (`github_projects.json`)

```json
{
  "total_count": 156,
  "repositories": [
    {
      "url": "https://github.com/django/django",
      "repo": "django/django",
      "description": "The Web framework for perfectionists with deadlines.",
      "stars": 76500,
      "language": "Python",
      "topics": ["web-framework", "python", "django"],
      "mentioned_in": [
        {
          "source": "逛逛GitHub",
          "article": "推荐10个Python框架",
          "context": "Django 是一个高级 Python Web 框架..."
        }
      ],
      "mention_count": 3
    }
  ]
}
```

### Markdown 报告 (`github_projects.md`)

```markdown
# GitHub 项目提取报告

## 📊 总体统计
- **总项目数（去重）**: 156

## 🔥 热门项目 (按 Stars 排序)

### 1. django/django
**URL**: https://github.com/django/django
**描述**: The Web framework for perfectionists with deadlines.
**⭐ Stars**: 76,500
**💻 Language**: Python
**🏷️ Topics**: `web-framework, python, django`
**📊 提及次数**: 3
**📚 来源公众号**: 逛逛GitHub, Python之禅
---
```

---

## 🎨 高级功能

### 查看统计信息

```bash
python extract_github.py --stats
```

输出：
- 按语言分类的项目数
- 最热门的项目（Top 20）
- 最常被提及的项目
- 按公众号分类的统计

### 按公众号筛选

```bash
python extract_github.py --source "逛逛GitHub"
```

### 按语言筛选

```bash
python extract_github.py --language Python
```

---

## 📁 文件结构

```
fetchWechat/
├── articles/               # 已下载的文章
│   ├── 逛逛GitHub/
│   │   ├── 文章1.md
│   │   ├── 文章2.md
│   │   └── ...
│   └── Python之禅/
│       └── ...
│
└── 提取结果（自动生成）:
    ├── github_projects.json    # 完整数据
    ├── github_projects.md      # Markdown 报告
    ├── github_projects.txt     # 简单列表
    └── github_extractor.log    # 日志
```

---

## 💡 实用场景

### 场景 1: 查找所有 Python 项目

```bash
python extract_github.py
# 然后查看 github_projects.md 中的语言分类
```

### 场景 2: 按 Stars 排序

```bash
python extract_github.py
# github_projects.md 的 "热门项目" 部分已按 Stars 排序
```

### 场景 3: 查找特定主题

在 `github_projects.json` 中搜索：
```bash
cat github_projects.json | jq '.repositories[] | select(.topics[] | contains("ai"))'
```

---

## 🔧 如果没有 GitHub Token

**也可以运行**，但会缺少：
- ⚠️ Stars 数量
- ⚠️ 语言信息
- ⚠️ Topics 标签
- ⚠️ 详细描述

**仍会提供**：
- ✅ GitHub URL
- ✅ 项目路径
- ✅ 文章中的上下文
- ✅ 提及次数
- ✅ 来源文章

---

## 📊 示例输出

运行后会看到：

```
$ python extract_github.py

============================================================
GitHub 项目提取器
============================================================

开始扫描: ./articles
找到 3 个公众号目录
  - 逛逛GitHub: 45 篇文章
  - Python之禅: 23 篇文章
  - 阮一峰的网络日志: 12 篇文章

开始提取 GitHub 项目...

[1/80] 处理: articles/逛逛GitHub/推荐10个项目.md
  找到 8 个项目

[2/80] 处理: articles/逛逛GitHub/开源工具.md
  找到 5 个项目

...

============================================================
提取完成!
============================================================
  总项目数（去重前）: 423
  总项目数（去重后）: 156
  
  已保存:
    - github_projects.json (完整数据)
    - github_projects.md (Markdown 报告)
    - github_projects.txt (简单列表)

🎉 完成！
```

---

## 🎯 下一步

### 数据分析

```python
import json

with open('github_projects.json', 'r') as f:
    data = json.load(f)

# 按语言统计
languages = {}
for repo in data['repositories']:
    lang = repo.get('language', 'Unknown')
    languages[lang] = languages.get(lang, 0) + 1

print(languages)
```

### 导出到 Excel

```bash
pip install pandas openpyxl

python << EOF
import json
import pandas as pd

with open('github_projects.json', 'r') as f:
    data = json.load(f)

df = pd.DataFrame(data['repositories'])
df.to_excel('github_projects.xlsx', index=False)
print("✅ 已导出到 github_projects.xlsx")
EOF
```

---

## ❓ 常见问题

### Q: 提取速度慢？
A: 如果配置了 GitHub Token，每个项目需要调用 API。默认有 0.1 秒延迟以避免速率限制。

### Q: 速率限制？
A: 
- 无 Token: 60 次/小时
- 有 Token: 5000 次/小时
建议配置 Token。

### Q: 如何更新数据？
A: 再次运行 `python extract_github.py` 会重新提取并覆盖旧文件。

---

**立即开始**: `python extract_github.py` 🚀
