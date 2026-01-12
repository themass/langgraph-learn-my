# 3 分钟上手指南

## 方案选择（30秒）

**快速决策**:
- 想要最简单？→ 用 **Selenium**（方案A）
- 想要最稳定？→ 用 **RSSHub**（方案B）
- 只要几篇？→ 用 **手动 URL**（方案C）

---

## 方案 A: Selenium（推荐新手）

### 1️⃣ 安装（1分钟）

```bash
cd fetchWechat
pip install selenium webdriver-manager
```

### 2️⃣ 运行（1分钟）

```bash
python scraper_selenium.py "Python之禅" 5
```

就这么简单！浏览器会自动打开，您可以看到整个过程。

### 💡 提示
- 如果出现验证码，手动完成后按 Enter 继续
- 首次运行会自动下载 ChromeDriver（需要几秒钟）

---

## 方案 B: RSSHub（推荐老手）

### 1️⃣ 获取 biz（30秒）

1. 打开任意一篇该公众号的文章
2. 查看 URL，复制 `__biz=` 后面的部分

例如：
```
https://mp.weixin.qq.com/s?__biz=MzI1NjU2NTU4MA==&...
                                 ^^^^^^^^^^^^^^^^
                                 复制这部分
```

### 2️⃣ 安装（30秒）

```bash
pip install feedparser
```

### 3️⃣ 运行（1分钟）

```bash
python scraper_rsshub.py "MzI1NjU2MTU4MA==" 10 "公众号名称"
```

---

## 方案 C: 手动 URL（最可靠）

### 1️⃣ 准备 URL 文件（1分钟）

在微信中打开文章 → 复制链接 → 粘贴到 `urls.txt`

```bash
cat > urls.txt << 'END'
https://mp.weixin.qq.com/s/xxx
https://mp.weixin.qq.com/s/yyy
END
```

### 2️⃣ 运行（1分钟）

```bash
python scrape_direct_urls.py urls.txt "公众号名称"
```

---

## 📂 查看结果

```bash
ls -lh articles/公众号名称/
```

所有文章已保存为 Markdown 格式！

---

## ❓ 遇到问题？

**常见问题**:
- Selenium: 确保安装了 Chrome 浏览器
- RSSHub: 确保 biz 参数正确
- Firecrawl: 确保服务运行 `curl http://localhost:3002/`

**详细文档**: 查看 [SOLUTIONS.md](./SOLUTIONS.md)

---

**3 分钟，开始抓取！** 🚀
