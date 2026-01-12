@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM LangGraph 学习项目完整依赖安装脚本 (Windows)
REM ========================================

echo 🚀 LangGraph 学习项目完整依赖安装脚本
echo ========================================

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未安装，请先安装 Python
    pause
    exit /b 1
)

echo ✅ Python 已安装
python --version

REM 检查是否在虚拟环境中
if defined VIRTUAL_ENV (
    echo ✅ 当前在虚拟环境中: %VIRTUAL_ENV%
) else (
    echo ⚠️  建议在虚拟环境中安装依赖
    echo    创建虚拟环境: python -m venv venv
    echo    激活虚拟环境: venv\Scripts\activate
    set /p continue="是否继续安装? (y/N): "
    if /i not "!continue!"=="y" (
        echo 安装已取消
        pause
        exit /b 0
    )
)

REM 升级 pip
echo 📦 升级 pip...
python -m pip install --upgrade pip

REM 检查 requirements.txt 是否存在
if not exist "requirements.txt" (
    echo ❌ requirements.txt 文件不存在
    pause
    exit /b 1
)

REM 安装依赖
echo 🔧 安装项目依赖...
echo 这可能需要几分钟时间，请耐心等待...

REM 分批安装依赖以避免超时
echo 📦 安装核心框架依赖...
pip install langgraph langchain langchain-core langchain-community langchain-openai langchain-ollama

echo 📦 安装 LLM 服务依赖...
pip install openai anthropic

echo 📦 安装向量数据库依赖...
pip install chromadb sentence-transformers huggingface-hub

echo 📦 安装 Web 框架依赖...
pip install streamlit gradio fastapi "uvicorn[standard]"

echo 📦 安装工具和搜索依赖...
pip install tavily-python requests python-dateutil

echo 📦 安装数据处理依赖...
pip install pandas numpy matplotlib seaborn

echo 📦 安装异步处理依赖...
pip install asyncio-mqtt aiohttp websockets

echo 📦 安装分布式计算依赖...
pip install "ray[default]"

echo 📦 安装其他工具依赖...
pip install pathlib2 watchdog python-dotenv pydantic typing-extensions

echo 📦 安装日志和调试工具...
pip install loguru rich

echo 📦 安装测试和开发工具...
pip install pytest pytest-asyncio black flake8

REM 验证安装
echo 🔍 验证关键依赖安装...
python -c "import langgraph; print('✅ LangGraph:', langgraph.__version__)" 2>nul || echo ❌ LangGraph 安装失败
python -c "import langchain; print('✅ LangChain:', langchain.__version__)" 2>nul || echo ❌ LangChain 安装失败
python -c "import openai; print('✅ OpenAI:', openai.__version__)" 2>nul || echo ❌ OpenAI 安装失败
python -c "import streamlit; print('✅ Streamlit:', streamlit.__version__)" 2>nul || echo ❌ Streamlit 安装失败

echo ✅ 所有依赖安装完成！
echo.
echo 📋 已安装的主要包:
pip list | findstr /i "langgraph langchain openai streamlit gradio fastapi chromadb ray"

echo.
echo 🎉 安装完成！现在可以运行学习示例了:
echo.
echo 📚 可运行的示例文件:
echo    python learn\第一个langgraph学习.py
echo    python learn\节点函数设计.py
echo    python learn\自主代理.py
echo    python learn\多Agent协作.py
echo    python learn\工具调用.py
echo    python learn\智能客服.py
echo    python learn\UI集成.py
echo.
echo 💡 重要提示:
echo    - 确保 Ollama 服务正在运行 (http://localhost:11434)
echo    - 或者配置 OpenAI API 密钥 (设置 OPENAI_API_KEY 环境变量)
echo    - 查看 README.md 了解更多使用说明
echo    - 运行 'python -m pytest' 进行测试

pause
