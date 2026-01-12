# PaddleOCR MCP 安装和配置指南

## ❌ 错误：spawn uvx ENOENT

如果遇到 `spawn uvx ENOENT` 错误，说明系统找不到 `uvx` 命令。

## 🔧 解决方案

### 方案一：安装 uv（推荐）

**macOS 安装：**

```bash
# 使用 Homebrew（推荐）
brew install uv

# 或使用官方安装脚本
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装后需要重启终端或重新加载 shell 配置
source ~/.zshrc  # 或 source ~/.bashrc
```

**验证安装：**

```bash
uv --version
uvx --version
```

**然后使用 uvx 配置：**

```json
{
  "mcpServers": {
    "PaddleOCR-VL": {
      "command": "uvx",
      "args": [
        "--from",
        "paddleocr-mcp",
        "paddleocr_mcp"
      ],
      "env": {
        "PADDLEOCR_MCP_PIPELINE": "PaddleOCR-VL",
        "PADDLEOCR_MCP_PPOCR_SOURCE": "aistudio",
        "PADDLEOCR_MCP_SERVER_URL": "https://a7l51bc4t3qfm6o6.aistudio-app.com",
        "PADDLEOCR_MCP_AISTUDIO_ACCESS_TOKEN": "your-access-token"
      }
    }
  }
}
```

### 方案二：使用 pip 安装（无需 uv）

**1. 安装 paddleocr-mcp：**

```bash
pip3 install -U paddleocr-mcp
```

**2. 验证安装：**

```bash
paddleocr_mcp --help
```

**3. 配置 Cursor（使用 python3 -m）：**

```json
{
  "mcpServers": {
    "PaddleOCR-VL": {
      "command": "python3",
      "args": [
        "-m",
        "paddleocr_mcp"
      ],
      "env": {
        "PADDLEOCR_MCP_PIPELINE": "PaddleOCR-VL",
        "PADDLEOCR_MCP_PPOCR_SOURCE": "aistudio",
        "PADDLEOCR_MCP_SERVER_URL": "https://a7l51bc4t3qfm6o6.aistudio-app.com",
        "PADDLEOCR_MCP_AISTUDIO_ACCESS_TOKEN": "your-access-token"
      }
    }
  }
}
```

**或者使用绝对路径：**

```bash
# 查找 paddleocr_mcp 的安装位置
which paddleocr_mcp
# 或
python3 -m pip show paddleocr-mcp | grep Location
```

然后使用完整路径：

```json
{
  "mcpServers": {
    "PaddleOCR-VL": {
      "command": "/path/to/paddleocr_mcp",
      "args": [],
      "env": {
        "PADDLEOCR_MCP_PIPELINE": "PaddleOCR-VL",
        "PADDLEOCR_MCP_PPOCR_SOURCE": "aistudio",
        "PADDLEOCR_MCP_SERVER_URL": "https://a7l51bc4t3qfm6o6.aistudio-app.com",
        "PADDLEOCR_MCP_AISTUDIO_ACCESS_TOKEN": "your-access-token"
      }
    }
  }
}
```

## ✅ 验证配置

配置完成后：

1. **重启 Cursor IDE**
2. **检查 MCP 服务器状态**
   - 应该显示为绿色（已连接）
3. **查看日志**
   - 如果仍有错误，检查 Cursor 的 MCP 日志

## 🔍 故障排查

### 问题1：找不到 python3

**解决：**
```bash
# 检查 python3 路径
which python3

# 如果找不到，可能需要安装 Python
# macOS: brew install python3
```

### 问题2：paddleocr_mcp 模块找不到

**解决：**
```bash
# 重新安装
pip3 install -U paddleocr-mcp

# 验证安装
python3 -m paddleocr_mcp --help
```

### 问题3：权限问题

**解决：**
```bash
# 使用用户安装（不需要 sudo）
pip3 install --user -U paddleocr-mcp
```
