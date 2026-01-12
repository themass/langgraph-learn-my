#!/bin/bash

# =============================================================================
# strongSwan Android 快速开始脚本
# 一键完成环境设置、测试和编译
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_banner() {
    echo -e "${PURPLE}"
    echo "=================================================="
    echo "    strongSwan Android 编译工具链"
    echo "=================================================="
    echo -e "${NC}"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# 检查脚本文件
check_scripts() {
    print_info "检查脚本文件..."
    
    local scripts=(
        "setup_strongswan_env.sh"
        "test_strongswan_env.sh"
        "build_strongswan_android.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [ -f "$script" ]; then
            if [ -x "$script" ]; then
                print_success "脚本存在且可执行: $script"
            else
                print_warning "脚本存在但不可执行: $script，正在添加执行权限..."
                chmod +x "$script"
            fi
        else
            print_error "脚本不存在: $script"
            exit 1
        fi
    done
}

# 显示菜单
show_menu() {
    echo
    print_info "请选择操作:"
    echo "  1) 设置编译环境"
    echo "  2) 测试编译环境"
    echo "  3) 编译 strongSwan"
    echo "  4) 完整流程 (设置+测试+编译)"
    echo "  5) 查看使用说明"
    echo "  6) 退出"
    echo
}

# 设置环境
setup_environment() {
    print_step "设置编译环境"
    ./setup_strongswan_env.sh
    
    if [ $? -eq 0 ]; then
        print_success "环境设置完成"
        echo
        print_info "请运行以下命令加载环境变量:"
        echo "  source ~/strongswan_env.sh"
        echo
        read -p "是否现在加载环境变量? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            source ~/strongswan_env.sh
            print_success "环境变量已加载"
        fi
    else
        print_error "环境设置失败"
        return 1
    fi
}

# 测试环境
test_environment() {
    print_step "测试编译环境"
    ./test_strongswan_env.sh
    
    if [ $? -eq 0 ]; then
        print_success "环境测试通过"
    else
        print_error "环境测试失败"
        return 1
    fi
}

# 编译 strongSwan
build_strongswan() {
    print_step "编译 strongSwan"
    
    # 检查环境变量
    if [ -z "$ANDROID_NDK_ROOT" ] || [ -z "$OPENSSL_SRC" ]; then
        print_error "环境变量未设置，请先运行环境设置"
        print_info "运行: source ~/strongswan_env.sh"
        return 1
    fi
    
    ./build_strongswan_android.sh
    
    if [ $? -eq 0 ]; then
        print_success "编译完成"
        echo
        print_info "输出文件位置:"
        echo "  $(pwd)/strongswan_build/output/"
        echo
        print_info "查看生成的文件:"
        find "$(pwd)/strongswan_build/output" -name "*.so" 2>/dev/null | head -10
    else
        print_error "编译失败"
        return 1
    fi
}

# 完整流程
full_process() {
    print_step "开始完整流程"
    
    # 1. 设置环境
    if ! setup_environment; then
        return 1
    fi
    
    # 2. 测试环境
    if ! test_environment; then
        return 1
    fi
    
    # 3. 编译
    if ! build_strongswan; then
        return 1
    fi
    
    print_success "完整流程执行成功！"
}

# 显示使用说明
show_usage() {
    echo
    print_info "使用说明:"
    echo
    echo "1. 环境设置 (setup_strongswan_env.sh)"
    echo "   - 安装必要的依赖包"
    echo "   - 下载 Android NDK r25c"
    echo "   - 下载 OpenSSL 3.1.0"
    echo "   - 下载 Android SDK 命令行工具"
    echo "   - 创建环境配置文件"
    echo
    echo "2. 环境测试 (test_strongswan_env.sh)"
    echo "   - 检查所有必要的命令和工具"
    echo "   - 验证环境变量设置"
    echo "   - 测试网络连接和磁盘空间"
    echo
    echo "3. 编译 strongSwan (build_strongswan_android.sh)"
    echo "   - 克隆 strongSwan 源码"
    echo "   - 构建 OpenSSL for Android"
    echo "   - 编译 Android 应用"
    echo "   - 提取 .so 文件"
    echo
    echo "4. 输出文件"
    echo "   - 生成的 .so 文件位于: strongswan_build/output/"
    echo "   - 包含多个架构: arm64-v8a, armeabi-v7a, x86, x86_64"
    echo "   - 包含使用说明: README.md"
    echo
    echo "5. 移植到其他项目"
    echo "   - 复制 .so 文件到 app/src/main/jniLibs/"
    echo "   - 配置 CMakeLists.txt"
    echo "   - 添加必要的权限"
    echo
    print_info "详细文档: STRONGSWAN_BUILD_GUIDE.md"
}

# 主循环
main() {
    print_banner
    
    # 检查脚本文件
    check_scripts
    
    while true; do
        show_menu
        read -p "请输入选择 (1-6): " choice
        
        case $choice in
            1)
                setup_environment
                ;;
            2)
                test_environment
                ;;
            3)
                build_strongswan
                ;;
            4)
                full_process
                ;;
            5)
                show_usage
                ;;
            6)
                print_info "退出"
                exit 0
                ;;
            *)
                print_error "无效选择，请输入 1-6"
                ;;
        esac
        
        echo
        read -p "按回车键继续..."
    done
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
