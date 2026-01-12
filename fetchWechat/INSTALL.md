# 安装指南

## 核心依赖（必需）

```bash
pip install firecrawl-py loguru requests beautifulsoup4 lxml
```

## 方案依赖（按需安装）

### 方案 1: Selenium

```bash
pip install selenium webdriver-manager
```

**验证安装**:
```bash
python3 -c "from scraper_selenium import SeleniumWeChatScraper; print('✅ Selenium 可用')"
```

### 方案 2: RSSHub

```bash
pip install feedparser
```

**验证安装**:
```bash
python3 -c "from scraper_rsshub import RSSHubScraper; print('✅ RSSHub 可用')"
```

### 方案 3: 手动 URL

无需额外依赖，使用核心依赖即可。

## 一键安装所有依赖

```bash
pip install -r requirements.txt
```

## 验证 Firecrawl 服务

```bash
curl http://localhost:3002/
# 应返回: {"message":"Firecrawl API"...}
```

## 快速测试

### 测试 Selenium

```bash
# 抓取 1 篇文章测试
python scraper_selenium.py "逛逛GitHub" 1
```

### 测试 RSSHub

```bash
# 先获取 biz 参数（查看 SOLUTIONS.md）
python scraper_rsshub.py help

# 测试抓取
python scraper_rsshub.py "your_biz_here" 1
```

### 测试手动 URL

```bash
# 创建测试 URL 文件
cat > test_urls.txt << 'EOF'
https://mp.weixin.qq.com/s/example
EOF

# 测试
python scrape_direct_urls.py test_urls.txt "测试"
```

## 故障排查

### Selenium 问题

**错误**: `ChromeDriver executable needs to be in PATH`

**解决**:
```bash
pip install --upgrade webdriver-manager
```

或手动下载: https://chromedriver.chromium.org/

### Firecrawl 问题

**错误**: `Connection refused`

**解决**:
```bash
# 启动 Firecrawl
cd /path/to/firecrawl
docker compose up -d

# 验证
curl http://localhost:3002/
```

### 依赖冲突

**建议**: 使用虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

## 完整安装流程（推荐）

```bash
# 1. 进入项目目录
cd fetchWechat

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 验证 Firecrawl
curl http://localhost:3002/

# 5. 测试 Selenium（推荐）
python scraper_selenium.py "逛逛GitHub" 1

# 完成！
```
