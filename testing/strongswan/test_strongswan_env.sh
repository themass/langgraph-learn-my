#!/bin/bash

# =============================================================================
# strongSwan Android 编译环境测试脚本
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 测试命令是否存在
test_command() {
    local cmd=$1
    local name=$2
    
    if command -v "$cmd" &> /dev/null; then
        print_success "$name 已安装: $(which $cmd)"
        return 0
    else
        print_error "$name 未安装"
        return 1
    fi
}

# 测试环境变量
test_environment() {
    print_info "测试环境变量..."
    
    local errors=0
    
    # 测试 ANDROID_NDK_ROOT
    if [ -n "$ANDROID_NDK_ROOT" ]; then
        if [ -d "$ANDROID_NDK_ROOT" ]; then
            print_success "ANDROID_NDK_ROOT: $ANDROID_NDK_ROOT"
        else
            print_error "ANDROID_NDK_ROOT 目录不存在: $ANDROID_NDK_ROOT"
            errors=$((errors + 1))
        fi
    else
        print_error "ANDROID_NDK_ROOT 未设置"
        errors=$((errors + 1))
    fi
    
    # 测试 OPENSSL_SRC
    if [ -n "$OPENSSL_SRC" ]; then
        if [ -d "$OPENSSL_SRC" ]; then
            print_success "OPENSSL_SRC: $OPENSSL_SRC"
        else
            print_error "OPENSSL_SRC 目录不存在: $OPENSSL_SRC"
            errors=$((errors + 1))
        fi
    else
        print_error "OPENSSL_SRC 未设置"
        errors=$((errors + 1))
    fi
    
    # 测试 ANDROID_SDK_ROOT (可选)
    if [ -n "$ANDROID_SDK_ROOT" ]; then
        if [ -d "$ANDROID_SDK_ROOT" ]; then
            print_success "ANDROID_SDK_ROOT: $ANDROID_SDK_ROOT"
        else
            print_warning "ANDROID_SDK_ROOT 目录不存在: $ANDROID_SDK_ROOT"
        fi
    else
        print_warning "ANDROID_SDK_ROOT 未设置 (可选)"
    fi
    
    return $errors
}

# 测试必要命令
test_commands() {
    print_info "测试必要命令..."
    
    local errors=0
    
    # 基础命令
    test_command "git" "Git" || errors=$((errors + 1))
    test_command "make" "Make" || errors=$((errors + 1))
    test_command "autoconf" "Autoconf" || errors=$((errors + 1))
    test_command "automake" "Automake" || errors=$((errors + 1))
    test_command "libtool" "Libtool" || errors=$((errors + 1))
    test_command "pkg-config" "pkg-config" || errors=$((errors + 1))
    test_command "cmake" "CMake" || errors=$((errors + 1))
    test_command "ninja" "Ninja" || errors=$((errors + 1))
    test_command "python3" "Python 3" || errors=$((errors + 1))
    test_command "jq" "jq" || errors=$((errors + 1))
    test_command "perl" "Perl" || errors=$((errors + 1))
    
    return $errors
}

# 测试 Android NDK
test_android_ndk() {
    print_info "测试 Android NDK..."
    
    if [ -z "$ANDROID_NDK_ROOT" ]; then
        print_error "ANDROID_NDK_ROOT 未设置"
        return 1
    fi
    
    local errors=0
    
    # 检查关键文件
    local key_files=(
        "ndk-build"
        "toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android21-clang"
        "toolchains/llvm/prebuilt/linux-x86_64/bin/armv7a-linux-androideabi16-clang"
        "toolchains/llvm/prebuilt/linux-x86_64/bin/x86_64-linux-android21-clang"
        "toolchains/llvm/prebuilt/linux-x86_64/bin/i686-linux-android16-clang"
    )
    
    for file in "${key_files[@]}"; do
        if [ -f "$ANDROID_NDK_ROOT/$file" ]; then
            print_success "NDK 文件存在: $file"
        else
            print_error "NDK 文件不存在: $file"
            errors=$((errors + 1))
        fi
    done
    
    # 测试编译器
    if [ -f "$ANDROID_NDK_ROOT/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android21-clang" ]; then
        local version=$("$ANDROID_NDK_ROOT/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android21-clang" --version 2>&1 | head -1)
        print_success "NDK 编译器版本: $version"
    fi
    
    return $errors
}

# 测试 OpenSSL
test_openssl() {
    print_info "测试 OpenSSL..."
    
    if [ -z "$OPENSSL_SRC" ]; then
        print_error "OPENSSL_SRC 未设置"
        return 1
    fi
    
    local errors=0
    
    # 检查关键文件
    local key_files=(
        "Configure"
        "config"
        "Makefile.in"
        "include/openssl/ssl.h"
        "include/openssl/crypto.h"
    )
    
    for file in "${key_files[@]}"; do
        if [ -f "$OPENSSL_SRC/$file" ]; then
            print_success "OpenSSL 文件存在: $file"
        else
            print_error "OpenSSL 文件不存在: $file"
            errors=$((errors + 1))
        fi
    done
    
    return $errors
}

# 测试磁盘空间
test_disk_space() {
    print_info "测试磁盘空间..."
    
    local available_space=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
    
    if [ "$available_space" -ge 5 ]; then
        print_success "可用磁盘空间: ${available_space}GB (足够)"
    else
        print_warning "可用磁盘空间: ${available_space}GB (建议至少 5GB)"
    fi
}

# 测试网络连接
test_network() {
    print_info "测试网络连接..."
    
    local test_urls=(
        "https://github.com"
        "https://dl.google.com"
        "https://www.openssl.org"
    )
    
    for url in "${test_urls[@]}"; do
        if curl -s --head "$url" > /dev/null; then
            print_success "网络连接正常: $url"
        else
            print_error "网络连接失败: $url"
            return 1
        fi
    done
    
    return 0
}

# 生成测试报告
generate_report() {
    local total_tests=$1
    local passed_tests=$2
    local failed_tests=$3
    
    echo
    print_info "测试报告"
    echo "=================================="
    echo "总测试数: $total_tests"
    echo "通过: $passed_tests"
    echo "失败: $failed_tests"
    echo "成功率: $(( passed_tests * 100 / total_tests ))%"
    echo
    
    if [ $failed_tests -eq 0 ]; then
        print_success "所有测试通过！可以开始编译 strongSwan"
        echo
        print_info "下一步:"
        echo "  1. 运行编译脚本: ./build_strongswan_android.sh"
        echo "  2. 等待编译完成 (可能需要 30-60 分钟)"
        echo "  3. 查看输出目录中的 .so 文件"
    else
        print_error "有 $failed_tests 个测试失败，请先解决这些问题"
        echo
        print_info "建议:"
        echo "  1. 运行环境设置脚本: ./setup_strongswan_env.sh"
        echo "  2. 检查网络连接和磁盘空间"
        echo "  3. 重新运行测试: ./test_strongswan_env.sh"
    fi
}

# 主函数
main() {
    print_info "开始测试 strongSwan Android 编译环境..."
    echo
    
    local total_tests=0
    local passed_tests=0
    local failed_tests=0
    
    # 测试命令
    total_tests=$((total_tests + 1))
    if test_commands; then
        passed_tests=$((passed_tests + 1))
    else
        failed_tests=$((failed_tests + 1))
    fi
    echo
    
    # 测试环境变量
    total_tests=$((total_tests + 1))
    if test_environment; then
        passed_tests=$((passed_tests + 1))
    else
        failed_tests=$((failed_tests + 1))
    fi
    echo
    
    # 测试 Android NDK
    total_tests=$((total_tests + 1))
    if test_android_ndk; then
        passed_tests=$((passed_tests + 1))
    else
        failed_tests=$((failed_tests + 1))
    fi
    echo
    
    # 测试 OpenSSL
    total_tests=$((total_tests + 1))
    if test_openssl; then
        passed_tests=$((passed_tests + 1))
    else
        failed_tests=$((failed_tests + 1))
    fi
    echo
    
    # 测试磁盘空间
    test_disk_space
    echo
    
    # 测试网络连接
    total_tests=$((total_tests + 1))
    if test_network; then
        passed_tests=$((passed_tests + 1))
    else
        failed_tests=$((failed_tests + 1))
    fi
    echo
    
    # 生成报告
    generate_report $total_tests $passed_tests $failed_tests
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
