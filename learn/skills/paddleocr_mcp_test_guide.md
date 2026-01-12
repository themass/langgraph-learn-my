# PaddleOCR MCP 服务测试指南

## 📋 测试方法总览

测试 PaddleOCR MCP 服务有多种方法，从简单到复杂：

1. **命令行直接测试** - 最快验证服务是否正常
2. **Python 脚本测试** - 完整测试 MCP 协议交互
3. **Cursor 集成测试** - 在实际使用环境中测试
4. **图片 OCR 测试** - 验证 OCR 功能是否正常

---

## 🚀 方法一：命令行直接测试（最快）

### 1. 测试 MCP 服务是否能启动

```bash
# 设置环境变量
export PADDLEOCR_MCP_PIPELINE="PaddleOCR-VL"
export PADDLEOCR_MCP_PPOCR_SOURCE="aistudio"
export PADDLEOCR_MCP_SERVER_URL="https://a7l51bc4t3qfm6o6.aistudio-app.com"
export PADDLEOCR_MCP_AISTUDIO_ACCESS_TOKEN="8fe361bcf0a2c5eae5ad6c250ce916972ef7c53e"

# 使用 Python 3.12.1 启动服务
/Users/liguoqing/.pyenv/versions/3.12.1/bin/python3 -m paddleocr_mcp
```

**预期结果：**
- 服务启动，等待 stdin 输入（这是正常的，MCP 通过 stdio 通信）
- 没有错误信息

**如果出现错误：**
- `No module named paddleocr_mcp` → 需要安装 `paddleocr-mcp`
- `ModuleNotFoundError: No module named 'redis.exceptions'` → 检查 Python 环境

### 2. 测试帮助信息

```bash
/Users/liguoqing/.pyenv/versions/3.12.1/bin/python3 -m paddleocr_mcp --help
```

**预期输出：**
```
usage: __main__.py [-h] [--pipeline {OCR,PP-StructureV3,PaddleOCR-VL}]
                   [--ppocr_source {local,aistudio,qianfan,self_hosted}]
                   ...
```

---

## 🐍 方法二：Python 脚本测试（推荐）

### 1. 安装依赖

```bash
pip install mcp
```

### 2. 基本连接测试

```bash
cd learn/skills
python3 test_paddleocr_mcp.py
```

**预期输出：**
```
📋 直接测试模式:
   Python: /Users/liguoqing/.pyenv/versions/3.12.1/bin/python3
   Env: {...}

🔗 正在连接到 PaddleOCR MCP 服务...
✅ MCP 服务连接成功！

📋 正在获取可用工具...
✅ 可用工具数量: X
   - paddleocr_vl: 描述...
   - ...

✅ 测试完成！
```

### 3. 使用 Cursor 配置测试

```bash
python3 test_paddleocr_mcp.py --cursor-mode
```

这会读取 `~/.cursor/mcp.json` 中的配置，模拟 Cursor 的实际调用。

### 4. 测试图片 OCR

```bash
# 使用项目中的测试图片
python3 test_paddleocr_mcp.py --image photos/erwei.jpg

# 或使用其他图片
python3 test_paddleocr_mcp.py --image /path/to/your/image.jpg
```

**预期输出：**
```
🖼️  使用图片测试: photos/erwei.jpg

🔧 调用工具: paddleocr_vl
📤 输入: photos/erwei.jpg

✅ OCR 结果:
[OCR 识别出的文本内容]
```

---

## 🎯 方法三：Cursor IDE 集成测试

### 1. 检查 MCP 服务状态

1. **打开 Cursor**
2. **查看 MCP 服务器状态**
   - 在 Cursor 设置中查看 MCP 服务器
   - 状态应该显示为 **绿色**（✅ 已连接）

### 2. 在 Cursor Chat 中测试

**测试 1：列出可用工具**
```
请列出 PaddleOCR-VL 服务的所有可用工具
```

**测试 2：OCR 识别**
```
请使用 PaddleOCR-VL 工具识别这张图片中的文字
[上传图片]
```

**测试 3：PDF 识别**
```
请使用 PaddleOCR-VL 工具提取这个 PDF 文件中的内容
[上传 PDF]
```

### 3. 检查 Cursor 日志

如果遇到问题，检查 Cursor 的 MCP 日志：

**macOS 日志位置：**
```
~/Library/Logs/Cursor/mcp.log
```

或者在 Cursor 中：
- `Cmd + Shift + P` → 搜索 "MCP" → 查看日志

---

## 🔍 方法四：详细诊断测试

### 1. 检查 Python 环境

```bash
# 检查 Python 版本
/Users/liguoqing/.pyenv/versions/3.12.1/bin/python3 --version
# 应该输出: Python 3.12.1

# 检查 paddleocr_mcp 是否安装
/Users/liguoqing/.pyenv/versions/3.12.1/bin/python3 -m paddleocr_mcp --help
```

### 2. 检查依赖包

```bash
# 检查 mcp 包
/Users/liguoqing/.pyenv/versions/3.12.1/bin/python3 -c "import mcp; print('mcp OK')"

# 检查 paddleocr_mcp
/Users/liguoqing/.pyenv/versions/3.12.1/bin/python3 -c "import paddleocr_mcp; print('paddleocr_mcp OK')"
```

### 3. 测试环境变量

```bash
# 设置环境变量
export PADDLEOCR_MCP_PIPELINE="PaddleOCR-VL"
export PADDLEOCR_MCP_PPOCR_SOURCE="aistudio"
export PADDLEOCR_MCP_SERVER_URL="https://a7l51bc4t3qfm6o6.aistudio-app.com"
export PADDLEOCR_MCP_AISTUDIO_ACCESS_TOKEN="8fe361bcf0a2c5eae5ad6c250ce916972ef7c53e"

# 验证环境变量
echo $PADDLEOCR_MCP_PIPELINE
echo $PADDLEOCR_MCP_SERVER_URL
```

### 4. 测试网络连接

```bash
# 测试是否能访问 AI Studio 服务
curl -X POST "https://a7l51bc4t3qfm6o6.aistudio-app.com/ocr" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 8fe361bcf0a2c5eae5ad6c250ce916972ef7c53e" \
  -d '{"image": "base64_encoded_image"}'
```

---

## 🐛 常见问题排查

### 问题 1: MCP 服务无法启动

**错误信息：**
```
/Users/liguoqing/.pyenv/versions/2.7.18/bin/python: No module named paddleocr_mcp
```

**原因：** 使用了错误的 Python 版本（2.7.18 而不是 3.12.1）

**解决方法：**
1. 检查 `~/.cursor/mcp.json` 中的 `command` 字段
2. 确保使用 Python 3.12.1 的绝对路径：
   ```json
   "command": "/Users/liguoqing/.pyenv/versions/3.12.1/bin/python3"
   ```
3. 重启 Cursor

### 问题 2: 模块导入错误

**错误信息：**
```
ModuleNotFoundError: No module named 'redis.exceptions'
```

**原因：** Python 路径中有本地 `redis` 目录干扰

**解决方法：**
```bash
# 查找并重命名本地 redis 目录
find ~ -name "redis" -type d -path "*/python/*" | grep -v site-packages
# 如果找到，重命名为 redis.bak
```

### 问题 3: 连接超时

**错误信息：**
```
Connection timeout
```

**原因：** 网络问题或服务地址错误

**解决方法：**
1. 检查 `PADDLEOCR_MCP_SERVER_URL` 是否正确
2. 检查网络连接
3. 验证访问令牌是否有效

### 问题 4: 工具未找到

**错误信息：**
```
Tool not found
```

**原因：** MCP 服务未正确启动或工具名称错误

**解决方法：**
1. 检查 MCP 服务状态（应该是绿色）
2. 使用测试脚本列出所有可用工具
3. 确认工具名称拼写正确

---

## ✅ 测试检查清单

### 基本测试
- [ ] Python 3.12.1 可以正常启动
- [ ] `paddleocr_mcp` 模块可以导入
- [ ] MCP 服务可以通过命令行启动
- [ ] Python 测试脚本可以连接服务
- [ ] 可以列出所有可用工具

### Cursor 集成测试
- [ ] Cursor MCP 配置正确
- [ ] MCP 服务状态显示为绿色
- [ ] 可以在 Cursor Chat 中调用工具
- [ ] OCR 功能可以正常识别图片

### 功能测试
- [ ] 可以识别图片中的文字
- [ ] 可以处理 PDF 文件
- [ ] 返回结果格式正确
- [ ] 错误处理正常

---

## 📚 相关资源

- [PaddleOCR MCP 官方文档](https://www.paddleocr.ai/latest/version3.x/deployment/mcp_server.html)
- [MCP 协议文档](https://modelcontextprotocol.io/)
- [Cursor MCP 配置指南](./paddleocr_mcp_integration.md)

---

## 🎉 测试成功后

如果所有测试都通过，恭喜！你的 PaddleOCR MCP 服务已经配置成功，可以在 Cursor 中使用了。

**下一步：**
1. 在 Cursor Chat 中尝试 OCR 功能
2. 上传图片或 PDF 进行识别
3. 探索其他功能（PP-StructureV3、PaddleOCR-VL 等）
