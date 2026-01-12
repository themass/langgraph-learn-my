# 微信公众号文章抓取 - 方案对比

## 📊 四种方案对比

| 方案 | 成功率 | 自动化 | 难度 | 推荐度 |
|------|--------|--------|------|--------|
| **方案1: Selenium** | **60-80%** | **✅ 全自动** | 中 | ⭐⭐⭐⭐⭐ |
| **方案2: RSSHub** | **90-100%** | **✅ 全自动** | 低 | ⭐⭐⭐⭐⭐ |
| 方案3: 手动URL | 100% | ❌ 手动 | 低 | ⭐⭐⭐ |
| 方案4: requests | < 5% | ✅ 全自动 | 低 | ❌ 不推荐 |

---

## 🚀 方案 1: Selenium 真实浏览器（推荐）

### 原理
使用真实浏览器环境，模拟人类操作，绕过搜狗反爬虫。

### 优势
- ✅ **全自动** - 输入公众号名称即可
- ✅ **成功率高** - 60-80%
- ✅ **可手动验证** - 遇到验证码可以手动完成
- ✅ **真实浏览器** - 完全模拟人类行为

### 使用方法

```bash
# 1. 安装依赖
pip install selenium webdriver-manager

# 2. 运行
python scraper_selenium.py "公众号名称" 10

# 浏览器会自动打开，可以看到整个过程
# 如果遇到验证码，会暂停等待您手动完成
```

### 特点
- 浏览器可见模式（可以看到操作过程）
- 自动跟踪搜狗重定向
- 支持手动处理验证码
- 慢速访问，避免触发反爬虫

### 适用场景
- ✅ 需要全自动抓取
- ✅ 可以接受较慢的速度
- ✅ 能够偶尔手动处理验证码

---

## 🌐 方案 2: RSSHub（最推荐）

### 原理
通过 RSSHub 服务订阅公众号，自动获取文章真实 URL。

### 优势
- ✅ **成功率最高** - 90-100%
- ✅ **最稳定** - 不受反爬虫影响
- ✅ **速度快** - 直接获取真实 URL
- ✅ **合规** - 使用 RSS 协议

### 使用方法

```bash
# 1. 安装依赖
pip install feedparser

# 2. 获取公众号 biz 参数
# 方法: 打开任意一篇该公众号的文章
# URL 示例: https://mp.weixin.qq.com/s?__biz=MzI1NjU2NTU4MA==&...
#                                            ^^^^^^^^^^^^^^^^
#                                            这就是 biz 参数

# 3. 运行
python scraper_rsshub.py "MzI1NjU2MTU4MA==" 10 "公众号名称"

# 或者获取 biz 帮助
python scraper_rsshub.py help
```

### 注意事项
- 需要获取公众号的 biz 参数（一次性工作）
- 可以使用公共 RSSHub 实例或自建
- 部分公众号可能没有开启消息列表

### 适用场景
- ✅ 愿意花 1 分钟获取 biz 参数
- ✅ 需要高成功率和稳定性
- ✅ 长期订阅同一公众号

---

## 📝 方案 3: 手动 URL 列表

### 原理
手动从微信复制文章 URL，批量抓取。

### 优势
- ✅ **100% 成功率**
- ✅ **内容完整**
- ✅ **简单可靠**

### 使用方法

```bash
# 1. 创建 urls.txt
cat > urls.txt << EOF
https://mp.weixin.qq.com/s/xxx
https://mp.weixin.qq.com/s/yyy
EOF

# 2. 运行
python scrape_direct_urls.py urls.txt "公众号名称"
```

### 适用场景
- ✅ 只需要少量文章（< 10 篇）
- ✅ 对特定文章有明确需求
- ❌ 不适合批量抓取（太累）

---

## ❌ 方案 4: requests（不推荐）

原 `scraper.py`，因搜狗反爬虫限制，成功率 < 5%。

---

## 🎯 推荐决策树

```
需要全自动？
├─ 是 → 能获取 biz 参数？
│       ├─ 是 → 【方案2: RSSHub】⭐⭐⭐⭐⭐
│       └─ 否 → 【方案1: Selenium】⭐⭐⭐⭐
└─ 否 → 文章数量多？
        ├─ 是 → 【方案1: Selenium】⭐⭐⭐⭐
        └─ 否 → 【方案3: 手动URL】⭐⭐⭐
```

---

## 💡 最佳实践

### 推荐组合

**情况1: 首次使用**
```bash
# 先用 Selenium 试试
python scraper_selenium.py "公众号名称" 5
```

**情况2: 长期订阅**
```bash
# 花 1 分钟获取 biz，然后用 RSSHub
python scraper_rsshub.py "biz参数" 20 "公众号名称"
```

**情况3: 只要几篇文章**
```bash
# 手动复制 URL
python scrape_direct_urls.py urls.txt "公众号名称"
```

---

## 📦 安装依赖

### 核心依赖（必需）
```bash
pip install firecrawl-py loguru requests beautifulsoup4 lxml
```

### Selenium 方案
```bash
pip install selenium webdriver-manager
```

### RSSHub 方案
```bash
pip install feedparser
```

### 全部安装
```bash
pip install -r requirements.txt
```

---

## 🔧 故障排查

### Selenium 问题

**Q: ChromeDriver 错误**
```bash
# 自动安装（推荐）
pip install webdriver-manager

# 或手动下载
# https://chromedriver.chromium.org/
```

**Q: 频繁触发验证码**
```
- 增加延迟时间（修改 time.sleep() 参数）
- 使用代理 IP
- 分批次抓取
```

### RSSHub 问题

**Q: RSS 返回空**
```
可能原因:
1. biz 参数不正确 → 重新获取
2. 公众号未开启消息列表 → 换用 Selenium 方案
3. RSSHub 服务不可用 → 尝试其他实例或自建
```

---

## 🎉 总结

### 最推荐方案

**日常使用**: 【方案2: RSSHub】
- 一次配置，长期使用
- 成功率最高，最稳定

**快速尝试**: 【方案1: Selenium】
- 立即开始，无需配置
- 全自动，成功率高

**应急方案**: 【方案3: 手动URL】
- 100% 可靠
- 适合少量文章

---

**现在您有 3 个可用方案，无需手动提供 URL！** 🚀
