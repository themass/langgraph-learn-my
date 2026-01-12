# LangGraph 学习项目安装指南

## 📋 项目概述

本项目包含完整的 LangGraph 学习示例，涵盖从基础概念到高级应用的各个方面。

## 🚀 快速开始

### 方法一：使用快速安装脚本（推荐）

#### Linux/macOS
```bash
# 给脚本添加执行权限
chmod +x install_dependencies.sh

# 运行安装脚本
./install_dependencies.sh
```

#### Windows
```cmd
# 运行安装脚本
install_dependencies.bat
```

#### 使用 Python 脚本
```bash
python quick_install.py
```

### 方法二：手动安装

#### 1. 环境准备

**创建虚拟环境（推荐）：**
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

#### 2. 安装依赖

**安装所有依赖：**
```bash
pip install -r requirements.txt
```

**或分步安装核心依赖：**
```bash
# 核心框架
pip install langgraph langchain langchain-core langchain-community langchain-openai langchain-ollama

# LLM 服务
pip install openai anthropic

# 向量数据库
pip install chromadb sentence-transformers huggingface-hub

# Web 框架
pip install streamlit gradio fastapi "uvicorn[standard]"

# 工具和搜索
pip install tavily-python requests python-dateutil

# 数据处理
pip install pandas numpy matplotlib seaborn

# 异步处理
pip install asyncio-mqtt aiohttp websockets

# 分布式计算
pip install "ray[default]"

# 其他工具
pip install pathlib2 watchdog python-dotenv pydantic typing-extensions

# 日志和调试
pip install loguru rich

# 测试和开发工具
pip install pytest pytest-asyncio black flake8
```

## 🔧 配置要求

### Python 版本
- **最低要求：** Python 3.8+
- **推荐版本：** Python 3.11+

### 系统要求
- **内存：** 至少 4GB RAM（推荐 8GB+）
- **存储：** 至少 2GB 可用空间
- **网络：** 稳定的互联网连接（用于下载模型和依赖）

## 🌐 外部服务配置

### 1. Ollama 服务（本地 LLM）

**安装 Ollama：**
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# 从 https://ollama.ai/download 下载安装包
```

**启动 Ollama 服务：**
```bash
ollama serve
```

**下载模型：**
```bash
# 下载常用模型
ollama pull llama3
ollama pull qwen:0.5b
ollama pull qwq:latest
```

### 2. OpenAI API（云端 LLM）

**设置 API 密钥：**
```bash
# Linux/macOS
export OPENAI_API_KEY="your-api-key-here"

# Windows
set OPENAI_API_KEY=your-api-key-here

# 或在 .env 文件中设置
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### 3. Tavily 搜索 API（可选）

**设置 API 密钥：**
```bash
export TAVILY_API_KEY="your-tavily-api-key"
```

## 📚 运行示例

### 基础示例
```bash
# 第一个 LangGraph 学习示例
python learn/第一个langgraph学习.py

# 节点函数设计
python learn/节点函数设计.py

# 状态设计详解
python learn/状态设计详解.py
```

### 高级示例
```bash
# 自主代理系统
python learn/自主代理.py

# 多 Agent 协作
python learn/多Agent协作.py

# 工具调用
python learn/工具调用.py

# 智能客服
python learn/智能客服.py
```

### Web 应用
```bash
# Streamlit UI
streamlit run learn/UI集成.py

# FastAPI 服务
python learn/UI集成.py --api

# Gradio 界面
python learn/UI集成.py --gradio
```

## 🧪 测试

**运行所有测试：**
```bash
python -m pytest
```

**运行特定测试：**
```bash
python -m pytest tests/ -v
```

## 🔍 故障排除

### 常见问题

#### 1. 依赖安装失败
```bash
# 升级 pip
pip install --upgrade pip

# 清理缓存
pip cache purge

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

#### 2. Ollama 连接失败
```bash
# 检查 Ollama 服务状态
curl http://localhost:11434/api/tags

# 重启 Ollama 服务
ollama serve
```

#### 3. 内存不足
```bash
# 使用较小的模型
ollama pull qwen:0.5b

# 或调整模型参数
# 在代码中设置 temperature=0.1, max_tokens=512
```

#### 4. 网络连接问题
```bash
# 设置代理（如果需要）
export HTTP_PROXY=http://proxy:port
export HTTPS_PROXY=http://proxy:port

# 或使用镜像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ package_name
```

### 日志和调试

**启用详细日志：**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**使用 Rich 进行美化输出：**
```python
from rich.console import Console
from rich.traceback import install

install()
console = Console()
```

## 📖 学习路径

### 初学者路径
1. `第一个langgraph学习.py` - 基础概念
2. `状态设计详解.py` - 状态管理
3. `节点函数设计.py` - 节点设计
4. `图结构与流程控制.py` - 流程控制

### 进阶路径
1. `自主代理.py` - 自主代理系统
2. `多Agent协作.py` - 多代理协作
3. `工具调用.py` - 工具集成
4. `智能客服.py` - 实际应用

### 高级路径
1. `性能优化.py` - 性能优化
2. `记忆与持久化.py` - 状态持久化
3. `流式输出.py` - 流式处理
4. `UI集成.py` - 用户界面

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 获取帮助

- 📖 查看 [README.md](README.md) 了解项目详情
- 🐛 报告问题：[GitHub Issues](https://github.com/your-repo/issues)
- 💬 讨论交流：[GitHub Discussions](https://github.com/your-repo/discussions)
- 📧 联系维护者：your-email@example.com

---

**祝您学习愉快！** 🎉
