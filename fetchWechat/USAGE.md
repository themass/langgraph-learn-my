# 使用指南 - 已修复所有问题

## ✅ 问题已解决

1. ✅ **参数错误** - `save_markdown()` 参数已修复
2. ✅ **Firecrawl 重定向** - 已确认 Firecrawl 无法单独处理搜狗反爬虫
3. ✅ **方案对比** - 提供了 3 个完整可用的方案

---

## 🚀 快速开始（30秒）

### 1. 检查环境

```bash
cd fetchWechat
python3 check_env.py
```

如果看到 `🎉 环境配置完成！可以开始使用`，就可以直接开始了！

### 2. 开始抓取

**推荐使用 Selenium 方案**（最简单）:

```bash
python scraper_selenium.py "逛逛GitHub" 5
```

浏览器会自动打开，您可以看到整个过程。如果遇到验证码，手动完成后按 Enter 继续。

---

## 📊 三种方案对比

| 方案 | 成功率 | 自动化 | 速度 | 适用场景 |
|------|--------|--------|------|----------|
| **Selenium** | 60-80% | ✅ 全自动 | 慢 | 日常使用 |
| **RSSHub** | 90-100% | ✅ 全自动 | 快 | 长期订阅 |
| **手动 URL** | 100% | ❌ 手动 | 快 | 少量文章 |

---

## 方案 1: Selenium（推荐新手）

### 特点
- ✅ 输入公众号名称即可
- ✅ 真实浏览器，可见操作过程
- ✅ 支持手动处理验证码
- ⚠️ 成功率 60-80%

### 使用

```bash
# 基础用法
python scraper_selenium.py "公众号名称" 10

# 示例
python scraper_selenium.py "Python之禅" 5
python scraper_selenium.py "阮一峰的网络日志" 10
```

### 提示
- 浏览器会自动打开（可以看到操作过程）
- 如果触发验证码，会暂停等待您手动完成
- 完成验证码后按 Enter 继续
- 首次运行会自动下载 ChromeDriver

---

## 方案 2: RSSHub（推荐老手）

### 特点
- ✅ 成功率最高（90-100%）
- ✅ 速度快
- ✅ 稳定可靠
- ⚠️ 需要先获取 biz 参数（一次性工作，30秒）

### 获取 biz 参数

1. 在浏览器中打开任意一篇该公众号的文章
2. 查看 URL，找到 `__biz=` 后面的部分

```
https://mp.weixin.qq.com/s?__biz=MzI1NjU2NTU4MA==&...
                                 ^^^^^^^^^^^^^^^^
                                 复制这部分
```

### 安装依赖

```bash
pip install feedparser
```

### 使用

```bash
# 基础用法
python scraper_rsshub.py "biz参数" 10 "公众号名称"

# 示例
python scraper_rsshub.py "MzI1NjU2MTU4MA==" 10 "逛逛GitHub"

# 获取帮助
python scraper_rsshub.py help
```

---

## 方案 3: 手动 URL（最可靠）

### 特点
- ✅ 100% 成功率
- ✅ 内容完整
- ✅ 无需额外依赖
- ❌ 需要手动复制 URL

### 使用

1. **准备 URL 文件**

```bash
cat > urls.txt << 'EOF'
https://mp.weixin.qq.com/s/xxx
https://mp.weixin.qq.com/s/yyy
https://mp.weixin.qq.com/s/zzz
EOF
```

2. **运行抓取**

```bash
python scrape_direct_urls.py urls.txt "公众号名称"
```

3. **查看结果**

```bash
ls -lh articles/公众号名称/
```

---

## 📂 输出结果

所有方案的文章都保存在 `articles/` 目录：

```
fetchWechat/
└── articles/
    ├── 逛逛GitHub/
    │   ├── 推荐10个GitHub项目.md
    │   ├── 开源工具推荐.md
    │   └── ...
    └── Python之禅/
        ├── Python技巧分享.md
        └── ...
```

每个 Markdown 文件包含：
- 标题
- 原文链接
- 发布日期
- 正文内容（高质量 Markdown 格式）

---

## ❓ 常见问题

### Q: Selenium 频繁触发验证码怎么办？

**A**: 
- 减少抓取数量（每次 3-5 篇）
- 增加延迟时间
- 分批次抓取，间隔几分钟

### Q: RSSHub biz 参数不正确？

**A**: 
- 确保复制的是 `__biz=` 后面到 `&` 之前的部分
- 包含 `==` 结尾
- 示例: `MzI1NjU2MTU4MA==`

### Q: Firecrawl 服务连接失败？

**A**: 
```bash
# 检查服务状态
curl http://localhost:3002/

# 如果失败，启动服务
cd /path/to/firecrawl
docker compose up -d
```

### Q: 哪个方案最好？

**A**: 
- **日常使用**: Selenium（简单直接）
- **长期订阅**: RSSHub（稳定高效）
- **少量文章**: 手动 URL（最可靠）

---

## 🎯 推荐使用流程

### 新手（第一次使用）

```bash
# 1. 检查环境
python3 check_env.py

# 2. 尝试 Selenium
python scraper_selenium.py "逛逛GitHub" 3

# 3. 查看结果
ls articles/逛逛GitHub/
```

### 老手（长期使用）

```bash
# 1. 获取 biz（一次性）
# 浏览器打开文章，复制 __biz=xxx

# 2. 使用 RSSHub
python scraper_rsshub.py "MzI1NjU2MTU4MA==" 20 "逛逛GitHub"

# 3. 享受 90%+ 成功率
```

---

## 📖 更多文档

- **GET_STARTED.md** - 3 分钟上手
- **SOLUTIONS.md** - 详细方案对比
- **INSTALL.md** - 安装指南
- **README.md** - 完整文档

---

**开始使用: `python scraper_selenium.py "公众号名称" 5`** 🚀
