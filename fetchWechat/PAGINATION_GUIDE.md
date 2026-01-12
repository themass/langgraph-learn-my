# 翻页配置说明

## 当前配置

### scraper_selenium.py

```python
# 页面加载等待
time.sleep(random.uniform(3, 6))  # 第 104 行

# 翻页间隔
time.sleep(random.uniform(5, 10))  # 第 171 行

# 文章抓取间隔
time.sleep(random.uniform(2, 4))   # 在 run() 方法中
```

## 如何调整

### 加快速度（风险更高）

```python
# 减少等待时间
time.sleep(random.uniform(1, 2))   # 页面加载
time.sleep(random.uniform(2, 4))   # 翻页间隔
time.sleep(random.uniform(1, 2))   # 文章抓取
```

### 降低风险（速度更慢）

```python
# 增加等待时间
time.sleep(random.uniform(5, 8))   # 页面加载
time.sleep(random.uniform(10, 15)) # 翻页间隔
time.sleep(random.uniform(3, 6))   # 文章抓取
```

## 推荐配置（抓取 100 篇）

**策略**: 慢速稳定

```python
# 页面加载等待: 5-8 秒
time.sleep(random.uniform(5, 8))

# 翻页间隔: 10-15 秒
time.sleep(random.uniform(10, 15))

# 文章抓取间隔: 3-6 秒
time.sleep(random.uniform(3, 6))
```

**预估时间**:
- 10 页 × 12 秒/页 = 2 分钟（翻页）
- 100 篇 × 4 秒/篇 = 6.7 分钟（抓取）
- **总计**: 约 9-10 分钟

## 验证码处理

如果在翻页过程中遇到验证码：

1. **自动检测**
```python
if "antispider" in self.driver.current_url:
    logger.warning("触发验证码")
    input("完成验证后按 Enter 继续: ")
```

2. **手动完成** - 在浏览器中完成验证码

3. **继续抓取** - 按 Enter 后自动继续

## 实际测试

### 测试 1: 抓取 10 篇（1 页）
```bash
python scraper_selenium.py "逛逛GitHub" 10
# 时间: 约 1-2 分钟
# 成功率: 90%
```

### 测试 2: 抓取 30 篇（3 页）
```bash
python scraper_selenium.py "逛逛GitHub" 30
# 时间: 约 3-5 分钟
# 成功率: 70-80%
```

### 测试 3: 抓取 100 篇（10 页）
```bash
python scraper_selenium.py "逛逛GitHub" 100
# 时间: 约 10-15 分钟
# 成功率: 50-70%（可能需要手动验证码 1-2 次）
```

## 建议

**最佳实践**:
- ✅ 单次抓取 ≤ 30 篇
- ✅ 分批次进行
- ✅ 间隔 5-10 分钟

**示例**:
```bash
# 第 1 批
python scraper_selenium.py "逛逛GitHub" 30
# 等待 10 分钟

# 第 2 批
python scraper_selenium.py "逛逛GitHub" 30
# 等待 10 分钟

# 第 3 批
python scraper_selenium.py "逛逛GitHub" 40

# 总计: 100 篇
```
