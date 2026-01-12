# 微信公众号文章采集器

> **✅ 新方案**: 提供 **Selenium** 和 **RSSHub** 两种全自动方案，无需手动提供 URL！详见 [SOLUTIONS.md](./SOLUTIONS.md)

输入**公众号名称**，自动搜索并批量抓取文章，保存为 Markdown 格式。

## 🚀 快速开始（三种方案）

| 方案 | 命令 | 成功率 | 说明 |
|------|------|--------|------|
| **Selenium** | `python scraper_selenium.py "公众号名称" 10` | 60-80% | 真实浏览器，全自动 |
| **RSSHub** | `python scraper_rsshub.py "biz参数" 10` | 90-100% | 需要 biz，最稳定 |
| 手动 URL | `python scrape_direct_urls.py urls.txt` | 100% | 需要手动复制 URL |

**👉 详细对比请查看 [SOLUTIONS.md](./SOLUTIONS.md)**

---

## ✨ 特性

- 🔍 **自动搜索** - 输入公众号名称，自动获取文章列表
- 🔥 **Firecrawl 引擎** - 高质量内容提取和清洗
- 📝 **Markdown 输出** - 自动转换为易读的 Markdown 格式  
- 🖼️ **图片提取** - 自动提取文章中的所有图片链接
- 📊 **元数据提取** - 获取标题、摘要、发布时间等信息
- 📁 **智能分类** - 按公众号名称自动分类保存
- ⚡ **批量处理** - 一次抓取多篇文章

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd fetchWechat
pip install -r requirements.txt
```

### 2. 启动 Firecrawl 服务

```bash
# 克隆 Firecrawl 官方仓库（如果还没有）
cd /path/to/workspace
git clone https://github.com/mendableai/firecrawl.git

# 启动服务
cd firecrawl
docker compose up -d

# 验证服务
curl http://localhost:3002/
# 应返回: {"message":"Firecrawl API","documentation_url":"https://docs.firecrawl.dev"}
```

### 3. 开始抓取

```bash
# 基本用法
python scraper.py <公众号名称> [抓取数量]

# 示例
python scraper.py "Python之禅" 10
python scraper.py "逛逛GitHub" 20
```

---

## 📋 使用说明

### 基本语法

```bash
python scraper.py <公众号名称> [抓取数量]
```

**参数说明**:
- `公众号名称`: 必填，要抓取的公众号名称
- `抓取数量`: 可选，默认 10 篇

### 使用示例

```bash
# 抓取 10 篇文章（默认）
python scraper.py "Python之禅"

# 抓取 20 篇文章
python scraper.py "逛逛GitHub" 20

# 抓取 50 篇文章
python scraper.py "阮一峰的网络日志" 50
```

### 输出结果

文章会保存到 `articles/` 目录：

```
fetchWechat/
└── articles/
    ├── Python之禅/
    │   ├── 文章标题1.md
    │   ├── 文章标题2.md
    │   └── ...
    └── 逛逛GitHub/
        ├── 推荐10个GitHub项目.md
        └── ...
```

---

## 🏗️ 工作流程

```
┌──────────────────┐
│  输入公众号名称   │
│  "Python之禅"    │
└─────────┬────────┘
          │
          ↓
┌──────────────────┐
│  搜狗微信搜索    │  自动搜索文章列表
│  (自动翻页)      │  获取标题、URL、摘要
└─────────┬────────┘
          │
          ↓
┌──────────────────┐
│  Firecrawl 抓取  │  • 高质量内容提取
│  (逐篇处理)      │  • HTML → Markdown
└─────────┬────────┘  • 图片链接提取
          │
          ↓
┌──────────────────┐
│  保存 Markdown   │
│  articles/公众号/ │
└──────────────────┘
```

---

## 🔧 配置说明

### 修改 Firecrawl 地址

编辑 `scraper.py` 的 `Config` 类：

```python
class Config:
    FIRECRAWL_URL = "http://localhost:3002"  # Firecrawl 服务地址
    OUTPUT_DIR = Path("articles")            # 输出目录
```

### 调整抓取参数

在 `scrape_article()` 方法中调整：

```python
result = self.firecrawl.scrape(
    url=url,
    formats=['markdown', 'html'],
    only_main_content=True,              # 只提取主要内容
    include_tags=['article', 'main'],    # 包含这些标签
    exclude_tags=['nav', 'footer'],      # 排除这些标签
    wait_for=3000,                       # 等待时间（毫秒）
)
```

### 调整延迟时间

在 `search_articles()` 方法中：

```python
# 搜索延迟（避免被封）
delay = random.uniform(3, 6)  # 3-6 秒随机延迟

# 抓取延迟
time.sleep(2)  # 每篇文章之间延迟 2 秒
```

---

## 📊 项目结构

```
fetchWechat/
├── scraper.py           # 核心采集脚本（单文件）
├── extract_github.py    # GitHub 项目提取工具
├── requirements.txt     # Python 依赖
├── .gitignore          # Git 配置
├── README.md           # 本文件
├── articles/           # 文章输出目录（自动创建）
│   └── 公众号名称/
│       ├── 文章1.md
│       └── 文章2.md
└── logs/               # 日志目录（自动创建）
    └── scraper_*.log
```

---

## 📝 Markdown 输出格式

```markdown
# 文章标题

**原文链接**: https://mp.weixin.qq.com/s/xxx
**发布时间**: 2024-01-01
**摘要**: 文章摘要内容...

---

## 正文标题

正文内容...

![图片](https://example.com/image.jpg)
```

---

## ❓ 常见问题

### Q: Firecrawl 服务无法连接？
**A**: 
1. 检查 Docker 是否运行：`docker ps | grep firecrawl`
2. 检查端口：`curl http://localhost:3002/`
3. 查看日志：`docker logs firecrawl-api`

### Q: 搜索不到文章？
**A**: 
1. 确认公众号名称正确
2. 可能触发了搜狗反爬虫（减少抓取数量，增加延迟）
3. 检查网络连接

### Q: 抓取失败或内容为空？
**A**: 
1. 搜狗重定向链接可能被拦截（正常现象，会自动跳过）
2. 增加 `wait_for` 时间等待页面加载
3. 查看日志文件了解详细错误

### Q: 如何避免被搜狗封禁？
**A**: 
1. 减少抓取数量（每次 5-10 篇）
2. 增加延迟时间（修改代码中的 `time.sleep()`）
3. 分批次抓取，间隔时间长一些

### Q: 能抓取所有公众号吗？
**A**: 
理论上可以，但搜狗微信搜索有反爬虫限制，建议：
- 每次抓取 10-20 篇
- 多次运行，分批抓取
- 遵守网站服务条款

---

## 🔥 Firecrawl 的作用

| 功能 | 说明 |
|------|------|
| 🧹 **内容清洗** | 自动移除广告、导航、页脚等无关内容 |
| 📝 **格式转换** | HTML → 高质量 Markdown（保留结构） |
| 🎯 **智能提取** | 识别文章标题、段落、列表、引用等 |
| 🖼️ **图片处理** | 提取所有图片链接（支持多种格式） |
| 📊 **元数据** | 提取标题、摘要、作者等信息 |

---

## 🔗 相关资源

- [Firecrawl 官方文档](https://docs.firecrawl.dev)
- [Firecrawl GitHub](https://github.com/mendableai/firecrawl)
- [firecrawl-py SDK](https://pypi.org/project/firecrawl-py/)

---

## ⚠️ 免责声明

本工具仅供学习和个人使用，请遵守相关法律法规和网站服务条款。
抓取内容的版权归原作者所有。

---

## 📄 许可证

MIT License

---

**一个命令，开始抓取！** 🚀

```bash
python scraper.py "公众号名称" 10
```

---

## 💡 **推荐: 直接抓取微信 URL 方案**

由于搜狗反爬虫限制，推荐使用直接抓取方案。

### 使用方法

1. **准备 URL 文件** (`urls.txt`):
   ```
   https://mp.weixin.qq.com/s/xxxxxxxxxxxx
   https://mp.weixin.qq.com/s/yyyyyyyyyyyy
   ```

2. **运行抓取**:
   ```bash
   python scrape_direct_urls.py urls.txt "公众号名称"
   ```

3. **查看结果**:
   ```
   articles/公众号名称/*.md
   ```

### 如何获取真实 URL?

- **微信客户端**: 文章右上角 "..." → "复制链接"
- **浏览器**: 访问公众号历史文章页面，手动复制链接
- **RSS**: 使用 RSSHub 等工具

**成功率: 100% ✅**

---

## 📊 两种方案对比

| 方案 | 成功率 | 优点 | 缺点 |
|------|--------|------|------|
| `scraper.py` (搜狗) | < 5% | 自动搜索 | ❌ 反爬虫限制 |
| `scrape_direct_urls.py` | 100% | ✅ 完整内容 | 需要手动获取 URL |

**建议: 使用 `scrape_direct_urls.py` 方案**

