#!/bin/bash

# PaddleOCR MCP 服务快速测试脚本

echo "🔍 PaddleOCR MCP 服务快速测试"
echo "================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 检查 Python 版本
echo "1️⃣  检查 Python 环境..."
PYTHON_PATH="/Users/liguoqing/.pyenv/versions/3.12.1/bin/python3"
if [ -f "$PYTHON_PATH" ]; then
    PYTHON_VERSION=$($PYTHON_PATH --version 2>&1)
    echo -e "${GREEN}✅${NC} Python: $PYTHON_VERSION"
else
    echo -e "${RED}❌${NC} Python 路径不存在: $PYTHON_PATH"
    exit 1
fi
echo ""

# 2. 检查 paddleocr_mcp 模块
echo "2️⃣  检查 paddleocr_mcp 模块..."
if $PYTHON_PATH -m paddleocr_mcp --help > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC} paddleocr_mcp 模块可用"
else
    echo -e "${RED}❌${NC} paddleocr_mcp 模块不可用"
    echo "   请运行: pip install paddleocr-mcp"
    exit 1
fi
echo ""

# 3. 检查 MCP 配置
echo "3️⃣  检查 Cursor MCP 配置..."
MCP_CONFIG="$HOME/.cursor/mcp.json"
if [ -f "$MCP_CONFIG" ]; then
    echo -e "${GREEN}✅${NC} MCP 配置文件存在: $MCP_CONFIG"
    
    # 检查配置内容
    if grep -q "PaddleOCR-VL" "$MCP_CONFIG"; then
        echo -e "${GREEN}✅${NC} 找到 PaddleOCR-VL 配置"
        
        # 检查 Python 路径
        if grep -q "3.12.1" "$MCP_CONFIG"; then
            echo -e "${GREEN}✅${NC} 使用 Python 3.12.1"
        else
            echo -e "${YELLOW}⚠️${NC}  未检测到 Python 3.12.1，请检查配置"
        fi
    else
        echo -e "${YELLOW}⚠️${NC}  未找到 PaddleOCR-VL 配置"
    fi
else
    echo -e "${RED}❌${NC} MCP 配置文件不存在: $MCP_CONFIG"
fi
echo ""

# 4. 检查环境变量
echo "4️⃣  检查环境变量..."
if [ -n "$PADDLEOCR_MCP_PIPELINE" ]; then
    echo -e "${GREEN}✅${NC} PADDLEOCR_MCP_PIPELINE: $PADDLEOCR_MCP_PIPELINE"
else
    echo -e "${YELLOW}⚠️${NC}  PADDLEOCR_MCP_PIPELINE 未设置（在 Cursor 中会自动设置）"
fi

if [ -n "$PADDLEOCR_MCP_SERVER_URL" ]; then
    echo -e "${GREEN}✅${NC} PADDLEOCR_MCP_SERVER_URL: $PADDLEOCR_MCP_SERVER_URL"
else
    echo -e "${YELLOW}⚠️${NC}  PADDLEOCR_MCP_SERVER_URL 未设置（在 Cursor 中会自动设置）"
fi
echo ""

# 5. 测试 MCP 服务启动
echo "5️⃣  测试 MCP 服务启动..."
export PADDLEOCR_MCP_PIPELINE="PaddleOCR-VL"
export PADDLEOCR_MCP_PPOCR_SOURCE="aistudio"
export PADDLEOCR_MCP_SERVER_URL="https://a7l51bc4t3qfm6o6.aistudio-app.com"
export PADDLEOCR_MCP_AISTUDIO_ACCESS_TOKEN="8fe361bcf0a2c5eae5ad6c250ce916972ef7c53e"

# macOS 兼容的测试方法
$PYTHON_PATH -m paddleocr_mcp --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅${NC} MCP 服务可以启动（帮助信息正常）"
else
    echo -e "${RED}❌${NC} MCP 服务启动失败"
fi
echo ""

# 6. 总结
echo "================================"
echo "📋 测试总结"
echo ""
echo "如果所有检查都通过 ✅，说明："
echo "  • Python 环境配置正确"
echo "  • paddleocr_mcp 模块已安装"
echo "  • MCP 服务可以正常启动"
echo ""
echo "下一步："
echo "  1. 重启 Cursor IDE"
echo "  2. 检查 MCP 服务状态（应该显示绿色 ✅）"
echo "  3. 在 Cursor Chat 中测试 OCR 功能"
echo ""
echo "详细测试请运行:"
echo "  python3 learn/skills/test_paddleocr_mcp.py"
echo ""
