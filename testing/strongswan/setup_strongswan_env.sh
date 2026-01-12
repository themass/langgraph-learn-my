#!/bin/bash

# =============================================================================
# strongSwan Android 编译环境设置脚本
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

# 检查操作系统
check_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        print_error "不支持的操作系统: $OSTYPE"
        exit 1
    fi
    print_info "检测到操作系统: $OS"
}

# 安装依赖包
install_dependencies() {
    print_info "安装编译依赖..."
    
    if [[ "$OS" == "linux" ]]; then
        # Ubuntu/Debian
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y \
                build-essential \
                autoconf \
                automake \
                libtool \
                pkg-config \
                git \
                wget \
                unzip \
                cmake \
                ninja-build \
                python3 \
                python3-pip \
                jq \
                make \
                perl
        # CentOS/RHEL
        elif command -v yum &> /dev/null; then
            sudo yum groupinstall -y "Development Tools"
            sudo yum install -y \
                autoconf \
                automake \
                libtool \
                pkgconfig \
                git \
                wget \
                unzip \
                cmake \
                ninja-build \
                python3 \
                python3-pip \
                jq \
                make \
                perl
        else
            print_error "不支持的 Linux 发行版"
            exit 1
        fi
    elif [[ "$OS" == "macos" ]]; then
        # 检查 Homebrew
        if ! command -v brew &> /dev/null; then
            print_info "安装 Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        
        # 安装依赖
        brew install \
            autoconf \
            automake \
            libtool \
            pkg-config \
            git \
            wget \
            cmake \
            ninja \
            python3 \
            jq \
            make \
            perl
    fi
    
    print_success "依赖包安装完成"
}

# 下载 Android NDK
download_android_ndk() {
    print_info "下载 Android NDK..."
    
    NDK_VERSION="r25c"
    NDK_DIR="$HOME/android-ndk-$NDK_VERSION"
    
    if [ -d "$NDK_DIR" ]; then
        print_warning "Android NDK 已存在: $NDK_DIR"
    else
        if [[ "$OS" == "linux" ]]; then
            NDK_URL="https://dl.google.com/android/repository/android-ndk-$NDK_VERSION-linux.zip"
        elif [[ "$OS" == "macos" ]]; then
            NDK_URL="https://dl.google.com/android/repository/android-ndk-$NDK_VERSION-darwin.zip"
        fi
        
        print_info "下载 Android NDK $NDK_VERSION..."
        wget -O "/tmp/android-ndk-$NDK_VERSION.zip" "$NDK_URL"
        
        print_info "解压 Android NDK..."
        unzip -q "/tmp/android-ndk-$NDK_VERSION.zip" -d "$HOME/"
        rm "/tmp/android-ndk-$NDK_VERSION.zip"
    fi
    
    export ANDROID_NDK_ROOT="$NDK_DIR"
    print_success "Android NDK 设置完成: $ANDROID_NDK_ROOT"
}

# 下载 OpenSSL
download_openssl() {
    print_info "下载 OpenSSL..."
    
    OPENSSL_VERSION="3.1.0"
    OPENSSL_DIR="$HOME/openssl-$OPENSSL_VERSION"
    
    if [ -d "$OPENSSL_DIR" ]; then
        print_warning "OpenSSL 已存在: $OPENSSL_DIR"
    else
        OPENSSL_URL="https://www.openssl.org/source/openssl-$OPENSSL_VERSION.tar.gz"
        
        print_info "下载 OpenSSL $OPENSSL_VERSION..."
        wget -O "/tmp/openssl-$OPENSSL_VERSION.tar.gz" "$OPENSSL_URL"
        
        print_info "解压 OpenSSL..."
        tar -xzf "/tmp/openssl-$OPENSSL_VERSION.tar.gz" -C "$HOME/"
        rm "/tmp/openssl-$OPENSSL_VERSION.tar.gz"
    fi
    
    export OPENSSL_SRC="$OPENSSL_DIR"
    print_success "OpenSSL 设置完成: $OPENSSL_SRC"
}

# 下载 Android SDK (可选)
download_android_sdk() {
    print_info "设置 Android SDK..."
    
    SDK_DIR="$HOME/Android/Sdk"
    
    if [ -d "$SDK_DIR" ]; then
        print_warning "Android SDK 已存在: $SDK_DIR"
    else
        print_info "创建 Android SDK 目录..."
        mkdir -p "$SDK_DIR"
        
        # 下载命令行工具
        if [[ "$OS" == "linux" ]]; then
            SDK_TOOLS_URL="https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip"
        elif [[ "$OS" == "macos" ]]; then
            SDK_TOOLS_URL="https://dl.google.com/android/repository/commandlinetools-mac-9477386_latest.zip"
        fi
        
        print_info "下载 Android SDK 命令行工具..."
        wget -O "/tmp/commandlinetools.zip" "$SDK_TOOLS_URL"
        
        print_info "解压 Android SDK 命令行工具..."
        unzip -q "/tmp/commandlinetools.zip" -d "$SDK_DIR/"
        rm "/tmp/commandlinetools.zip"
        
        # 设置目录结构
        mkdir -p "$SDK_DIR/cmdline-tools/latest"
        mv "$SDK_DIR/cmdline-tools/bin" "$SDK_DIR/cmdline-tools/latest/"
        mv "$SDK_DIR/cmdline-tools/lib" "$SDK_DIR/cmdline-tools/latest/"
    fi
    
    export ANDROID_SDK_ROOT="$SDK_DIR"
    print_success "Android SDK 设置完成: $ANDROID_SDK_ROOT"
}

# 创建环境配置文件
create_env_file() {
    print_info "创建环境配置文件..."
    
    cat > "$HOME/strongswan_env.sh" << EOF
#!/bin/bash
# strongSwan Android 编译环境配置

export ANDROID_NDK_ROOT="$ANDROID_NDK_ROOT"
export ANDROID_SDK_ROOT="$ANDROID_SDK_ROOT"
export OPENSSL_SRC="$OPENSSL_SRC"
export NDK_DIR="$ANDROID_NDK_ROOT"

# 添加到 PATH
export PATH="\$ANDROID_NDK_ROOT/toolchains/llvm/prebuilt/linux-x86_64/bin:\$PATH"
export PATH="\$ANDROID_SDK_ROOT/cmdline-tools/latest/bin:\$PATH"

echo "strongSwan Android 编译环境已加载"
echo "ANDROID_NDK_ROOT: \$ANDROID_NDK_ROOT"
echo "ANDROID_SDK_ROOT: \$ANDROID_SDK_ROOT"
echo "OPENSSL_SRC: \$OPENSSL_SRC"
EOF

    chmod +x "$HOME/strongswan_env.sh"
    print_success "环境配置文件创建完成: $HOME/strongswan_env.sh"
}

# 验证环境
verify_environment() {
    print_info "验证编译环境..."
    
    # 检查 NDK
    if [ -f "$ANDROID_NDK_ROOT/ndk-build" ]; then
        print_success "Android NDK 验证通过"
    else
        print_error "Android NDK 验证失败"
        exit 1
    fi
    
    # 检查 OpenSSL
    if [ -f "$OPENSSL_SRC/Configure" ]; then
        print_success "OpenSSL 验证通过"
    else
        print_error "OpenSSL 验证失败"
        exit 1
    fi
    
    # 检查 SDK
    if [ -d "$ANDROID_SDK_ROOT/cmdline-tools" ]; then
        print_success "Android SDK 验证通过"
    else
        print_warning "Android SDK 验证失败，但不影响编译"
    fi
}

# 显示使用说明
show_usage() {
    print_success "环境设置完成！"
    echo
    print_info "使用方法:"
    echo "  1. 加载环境变量:"
    echo "     source ~/strongswan_env.sh"
    echo
    echo "  2. 运行编译脚本:"
    echo "     ./build_strongswan_android.sh"
    echo
    print_info "环境变量:"
    echo "  ANDROID_NDK_ROOT: $ANDROID_NDK_ROOT"
    echo "  ANDROID_SDK_ROOT: $ANDROID_SDK_ROOT"
    echo "  OPENSSL_SRC: $OPENSSL_SRC"
    echo
    print_info "注意事项:"
    echo "  - 确保有足够的磁盘空间 (至少 5GB)"
    echo "  - 编译过程可能需要 30-60 分钟"
    echo "  - 建议在稳定的网络环境下进行"
}

# 主函数
main() {
    print_info "开始设置 strongSwan Android 编译环境..."
    echo
    
    # 检查操作系统
    check_os
    
    # 安装依赖
    install_dependencies
    
    # 下载必要工具
    download_android_ndk
    download_openssl
    download_android_sdk
    
    # 创建环境配置
    create_env_file
    
    # 验证环境
    verify_environment
    
    # 显示使用说明
    show_usage
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
