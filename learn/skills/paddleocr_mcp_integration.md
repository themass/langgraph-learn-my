# PaddleOCR MCP 服务集成到 Cursor 指南

## 📋 概述

PaddleOCR MCP 服务器提供了 OCR、PP-StructureV3 和 PaddleOCR-VL 等功能，可以集成到 Cursor IDE 中使用。

## 🚀 快速开始

### 方式一：使用 uvx（推荐，无需安装）

#### 1. 安装 uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或使用 Homebrew (macOS)
brew install uv
```

#### 2. 配置 Cursor

在 Cursor 的配置文件中添加 MCP 服务器配置：

**macOS 配置文件位置：**
```
~/Library/Application Support/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json
```

**或者项目级配置：**
```
.cursor/mcp.json
```

**配置示例（PaddleOCR 官网服务模式）：**

```json
{
  "mcpServers": {
    "paddleocr-ocr": {
      "command": "uvx",
      "args": [
        "--from",
        "paddleocr-mcp",
        "paddleocr_mcp"
      ],
      "env": {
        "PADDLEOCR_MCP_PIPELINE": "OCR",
        "PADDLEOCR_MCP_PPOCR_SOURCE": "aistudio",
        "PADDLEOCR_MCP_SERVER_URL": "<your-server-url>",
        "PADDLEOCR_MCP_AISTUDIO_ACCESS_TOKEN": "<your-access-token>"
      }
    }
  }
}
```

**配置示例（本地 Python 库模式）：**

```json
{
  "mcpServers": {
    "paddleocr-ocr": {
      "command": "uvx",
      "args": [
        "--from",
        "paddleocr-mcp[local-cpu]",
        "paddleocr_mcp"
      ],
      "env": {
        "PADDLEOCR_MCP_PIPELINE": "OCR",
        "PADDLEOCR_MCP_PPOCR_SOURCE": "local"
      }
    }
  }
}
```

### 方式二：使用 pip 安装

#### 1. 安装 paddleocr-mcp

```bash
# 基础安装
pip install -U paddleocr-mcp

# 包含 PaddleOCR（不包含飞桨框架）
pip install "paddleocr-mcp[local]"

# 包含 PaddleOCR 和 CPU 版本飞桨框架
pip install "paddleocr-mcp[local-cpu]"
```

#### 2. 验证安装

```bash
paddleocr_mcp --help
```

#### 3. 配置 Cursor

**配置示例：**

```json
{
  "mcpServers": {
    "paddleocr-ocr": {
      "command": "paddleocr_mcp",
      "args": [],
      "env": {
        "PADDLEOCR_MCP_PIPELINE": "OCR",
        "PADDLEOCR_MCP_PPOCR_SOURCE": "local"
      }
    }
  }
}
```

**注意：** 如果 `paddleocr_mcp` 无法在系统 PATH 中找到，请将 `command` 设置为可执行文件的绝对路径。

## 🔧 工作模式配置

### 模式一：本地 Python 库

**适用场景：**
- 需要离线使用
- 对数据隐私有严格要求
- 本地环境性能充足

**配置：**

```json
{
  "mcpServers": {
    "paddleocr-ocr": {
      "command": "uvx",
      "args": [
        "--from",
        "paddleocr-mcp[local-cpu]",
        "paddleocr_mcp"
      ],
      "env": {
        "PADDLEOCR_MCP_PIPELINE": "OCR",
        "PADDLEOCR_MCP_PPOCR_SOURCE": "local"
      }
    }
  }
}
```

**性能优化提示：**
- OCR 产线：建议使用 `mobile` 系列模型
- PP-StructureV3：关闭不需要的功能，使用轻量级模型

### 模式二：PaddleOCR 官网服务

**适用场景：**
- 快速体验功能
- 快速验证方案
- 零代码开发场景

**配置步骤：**

1. **获取服务基础 URL 和访问令牌**
   - 访问：https://aistudio.baidu.com/paddleocr/task
   - 点击左上角的"API"
   - 复制"文字识别（PP-OCRv5）"对应的 `API_URL`
   - 去掉端点末尾（`/ocr`）的部分，即服务的基础 URL
   - 复制 `TOKEN`（访问令牌）

2. **配置 Cursor**

```json
{
  "mcpServers": {
    "paddleocr-ocr": {
      "command": "uvx",
      "args": [
        "--from",
        "paddleocr-mcp",
        "paddleocr_mcp"
      ],
      "env": {
        "PADDLEOCR_MCP_PIPELINE": "OCR",
        "PADDLEOCR_MCP_PPOCR_SOURCE": "aistudio",
        "PADDLEOCR_MCP_SERVER_URL": "https://xxxxxx.aistudio-app.com",
        "PADDLEOCR_MCP_AISTUDIO_ACCESS_TOKEN": "your-access-token"
      }
    }
  }
}
```

### 模式三：千帆平台服务

**适用场景：**
- 使用百度智能云千帆大模型平台

**配置：**

```json
{
  "mcpServers": {
    "paddleocr-vl": {
      "command": "uvx",
      "args": [
        "--from",
        "paddleocr-mcp",
        "paddleocr_mcp"
      ],
      "env": {
        "PADDLEOCR_MCP_PIPELINE": "PaddleOCR-VL",
        "PADDLEOCR_MCP_PPOCR_SOURCE": "qianfan",
        "PADDLEOCR_MCP_SERVER_URL": "https://qianfan.baidubce.com/v2/ocr",
        "PADDLEOCR_MCP_QIANFAN_API_KEY": "your-api-key"
      }
    }
  }
}
```

**注意：** 千帆平台服务目前仅支持 PaddleOCR-VL 和 PP-StructureV3。

### 模式四：自托管服务

**适用场景：**
- 需要自定义服务配置
- 对数据隐私有严格要求
- 已有自托管的 PaddleOCR 服务

**配置：**

```json
{
  "mcpServers": {
    "paddleocr-ocr": {
      "command": "uvx",
      "args": [
        "--from",
        "paddleocr-mcp",
        "paddleocr_mcp"
      ],
      "env": {
        "PADDLEOCR_MCP_PIPELINE": "OCR",
        "PADDLEOCR_MCP_PPOCR_SOURCE": "self_hosted",
        "PADDLEOCR_MCP_SERVER_URL": "http://127.0.0.1:8000"
      }
    }
  }
}
```

## 📝 参数说明

### 环境变量

| 环境变量 | 命令行参数 | 类型 | 描述 | 可选值 | 默认值 |
|---------|-----------|------|------|--------|--------|
| `PADDLEOCR_MCP_PIPELINE` | `--pipeline` | str | 要运行的产线 | `"OCR"`, `"PP-StructureV3"`, `"PaddleOCR-VL"` | `"OCR"` |
| `PADDLEOCR_MCP_PPOCR_SOURCE` | `--ppocr_source` | str | PaddleOCR 能力来源 | `"local"`, `"aistudio"`, `"qianfan"`, `"self_hosted"` | `"local"` |
| `PADDLEOCR_MCP_SERVER_URL` | `--server_url` | str | 底层服务基础 URL | - | None |
| `PADDLEOCR_MCP_AISTUDIO_ACCESS_TOKEN` | `--aistudio_access_token` | str | AI Studio 访问令牌 | - | None |
| `PADDLEOCR_MCP_TIMEOUT` | `--timeout` | int | 请求超时时间（秒） | - | 60 |
| `PADDLEOCR_MCP_DEVICE` | `--device` | str | 运行推理的设备（仅 local 模式） | - | None |
| `PADDLEOCR_MCP_PIPELINE_CONFIG` | `--pipeline_config` | str | 产线配置文件路径（仅 local 模式） | - | None |

### 命令行参数

| 参数 | 类型 | 描述 | 默认值 |
|------|------|------|--------|
| `--http` | bool | 使用 Streamable HTTP 传输而非 stdio | False |
| `--host` | str | Streamable HTTP 模式的主机地址 | `"127.0.0.1"` |
| `--port` | int | Streamable HTTP 模式的端口 | 8000 |
| `--verbose` | bool | 启用详细日志记录 | False |

## 🎯 支持的工具

### OCR
- 对图像和 PDF 文件进行文本检测与识别

### PP-StructureV3
- 从图像或 PDF 文件中识别和提取文本块、标题、段落、图片、表格以及其他版面元素
- 将输入转换为 Markdown 文档

### PaddleOCR-VL
- 使用基于多模态大模型的方案
- 从图像或 PDF 文件中识别和提取文本块、标题、段落、图片、表格以及其他版面元素
- 将输入转换为 Markdown 文档

## 📍 Cursor 配置文件位置

### macOS
```
~/Library/Application Support/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json
```

### Windows
```
%APPDATA%\Cursor\User\globalStorage\rooveterinaryinc.roo-cline\settings\cline_mcp_settings.json
```

### Linux
```
~/.config/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json
```

### 项目级配置（推荐）

在项目根目录创建 `.cursor/mcp.json` 文件：

```json
{
  "mcpServers": {
    "paddleocr-ocr": {
      "command": "uvx",
      "args": [
        "--from",
        "paddleocr-mcp",
        "paddleocr_mcp"
      ],
      "env": {
        "PADDLEOCR_MCP_PIPELINE": "OCR",
        "PADDLEOCR_MCP_PPOCR_SOURCE": "aistudio",
        "PADDLEOCR_MCP_SERVER_URL": "https://xxxxxx.aistudio-app.com",
        "PADDLEOCR_MCP_AISTUDIO_ACCESS_TOKEN": "your-access-token"
      }
    }
  }
}
```

**注意：** 项目级配置会覆盖全局配置。

## ✅ 验证配置

配置完成后：

1. **重启 Cursor IDE**
2. **检查 MCP 服务器状态**
   - 在 Cursor 的设置中查看 MCP 服务器状态
   - 应该显示为绿色（已连接）

3. **测试工具**
   - 在 Cursor 中尝试使用 OCR 功能
   - 例如：上传一张图片，让 Cursor 识别其中的文字
   - 或使用命令：`请使用 paddleocr-ocr 工具识别这张图片中的文字`

## 🔍 故障排查

### 问题1：MCP 服务器无法启动

**解决：**
- 检查 `command` 路径是否正确
- 检查 `uvx` 是否已安装
- 检查环境变量配置是否正确

### 问题2：无法连接到服务

**解决：**
- 检查 `PADDLEOCR_MCP_SERVER_URL` 是否正确
- 检查 `PADDLEOCR_MCP_AISTUDIO_ACCESS_TOKEN` 是否有效
- 检查网络连接

### 问题3：本地模式性能问题

**解决：**
- 使用轻量级模型（mobile 系列）
- 关闭不需要的功能
- 调整产线配置

## 📚 参考资源

- [PaddleOCR MCP 服务器官方文档](https://www.paddleocr.ai/latest/version3.x/deployment/mcp_server.html)
- [PaddleOCR GitHub](https://github.com/PaddlePaddle/PaddleOCR)
- [uv 官方文档](https://docs.astral.sh/uv/)
