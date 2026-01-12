#!/bin/bash

# LangGraph 学习项目完整依赖安装脚本
# ========================================

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 未安装，请先安装 $1"
        exit 1
    fi
}

# 主安装流程
main() {
    echo "🚀 LangGraph 学习项目完整依赖安装脚本"
    echo "========================================"
    
    # 检查基本命令
    print_info "检查基本命令..."
    check_command python
    check_command pip
    
    # 检查 Python 版本
    print_info "检查 Python 版本..."
    python_version=$(python --version 2>&1)
    print_success "当前 Python 版本: $python_version"
    
    # 检查是否在虚拟环境中
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        print_success "当前在虚拟环境中: $VIRTUAL_ENV"
    else
        print_warning "建议在虚拟环境中安装依赖"
        echo "   创建虚拟环境: python -m venv venv"
        echo "   激活虚拟环境: source venv/bin/activate (Linux/Mac) 或 venv\\Scripts\\activate (Windows)"
        read -p "是否继续安装? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "安装已取消"
            exit 0
        fi
    fi
    
    # 升级 pip
    print_info "升级 pip..."
    pip install --upgrade pip
    
    # 检查 requirements.txt 是否存在
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt 文件不存在"
        exit 1
    fi
    
    # 安装依赖
    print_info "安装项目依赖..."
    print_info "这可能需要几分钟时间，请耐心等待..."
    
    # 分批安装依赖以避免超时
    print_info "安装核心框架依赖..."
    pip install langgraph langchain langchain-core langchain-community langchain-openai langchain-ollama
    
    print_info "安装 LLM 服务依赖..."
    pip install openai anthropic
    
    print_info "安装向量数据库依赖..."
    pip install chromadb sentence-transformers huggingface-hub
    
    print_info "安装 Web 框架依赖..."
    pip install streamlit gradio fastapi "uvicorn[standard]"
    
    print_info "安装工具和搜索依赖..."
    pip install tavily-python requests python-dateutil
    
    print_info "安装数据处理依赖..."
    pip install pandas numpy matplotlib seaborn
    
    print_info "安装异步处理依赖..."
    pip install asyncio-mqtt aiohttp websockets
    
    print_info "安装分布式计算依赖..."
    pip install "ray[default]"
    
    print_info "安装其他工具依赖..."
    pip install pathlib2 watchdog python-dotenv pydantic typing-extensions
    
    print_info "安装日志和调试工具..."
    pip install loguru rich
    
    print_info "安装测试和开发工具..."
    pip install pytest pytest-asyncio black flake8
    
    # 验证安装
    print_info "验证关键依赖安装..."
    python -c "import langgraph; print('✅ LangGraph:', langgraph.__version__)" || print_error "LangGraph 安装失败"
    python -c "import langchain; print('✅ LangChain:', langchain.__version__)" || print_error "LangChain 安装失败"
    python -c "import openai; print('✅ OpenAI:', openai.__version__)" || print_error "OpenAI 安装失败"
    python -c "import streamlit; print('✅ Streamlit:', streamlit.__version__)" || print_error "Streamlit 安装失败"
    
    print_success "所有依赖安装完成！"
    echo ""
    echo "📋 已安装的主要包:"
    pip list | grep -E "(langgraph|langchain|openai|streamlit|gradio|fastapi|chromadb|ray)" | head -10
    
    echo ""
    print_success "🎉 安装完成！现在可以运行学习示例了:"
    echo ""
    echo "📚 可运行的示例文件:"
    echo "   python learn/第一个langgraph学习.py"
    echo "   python learn/节点函数设计.py"
    echo "   python learn/自主代理.py"
    echo "   python learn/多Agent协作.py"
    echo "   python learn/工具调用.py"
    echo "   python learn/智能客服.py"
    echo "   python learn/UI集成.py"
    echo ""
    echo "💡 重要提示:"
    echo "   - 确保 Ollama 服务正在运行 (http://localhost:11434)"
    echo "   - 或者配置 OpenAI API 密钥 (设置 OPENAI_API_KEY 环境变量)"
    echo "   - 查看 README.md 了解更多使用说明"
    echo "   - 运行 'python -m pytest' 进行测试"
}

# 运行主函数
main "$@"
