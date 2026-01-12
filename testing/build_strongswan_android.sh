#!/bin/bash

# =============================================================================
# strongSwan Android 编译脚本
# 用于编译 strongSwan Android VPN 客户端的 .so 文件，可移植到其他项目
# 基于官方文档: https://docs.strongswan.org/docs/latest/os/androidVpnClientBuild.html
# =============================================================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
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

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 命令未找到，请先安装"
        exit 1
    fi
}

# 检查环境变量
check_environment() {
    print_info "检查编译环境..."
    
    # 检查必要的命令
    check_command "git"
    check_command "make"
    check_command "autoconf"
    check_command "automake"
    check_command "libtool"
    check_command "pkg-config"
    
    # 检查环境变量
    if [ -z "$ANDROID_NDK_ROOT" ]; then
        print_error "请设置 ANDROID_NDK_ROOT 环境变量"
        print_info "例如: export ANDROID_NDK_ROOT=/path/to/android-ndk-r25c"
        exit 1
    fi
    
    if [ -z "$OPENSSL_SRC" ]; then
        print_error "请设置 OPENSSL_SRC 环境变量"
        print_info "例如: export OPENSSL_SRC=/path/to/openssl-3.1.0"
        exit 1
    fi
    
    if [ ! -d "$ANDROID_NDK_ROOT" ]; then
        print_error "Android NDK 目录不存在: $ANDROID_NDK_ROOT"
        exit 1
    fi
    
    if [ ! -d "$OPENSSL_SRC" ]; then
        print_error "OpenSSL 源码目录不存在: $OPENSSL_SRC"
        exit 1
    fi
    
    print_success "环境检查通过"
}

# 创建目录结构
create_directories() {
    print_info "创建目录结构..."
    
    # 创建工作目录
    WORK_DIR=$(pwd)/strongswan_build
    mkdir -p "$WORK_DIR"
    cd "$WORK_DIR"
    
    # 创建输出目录
    OUTPUT_DIR="$WORK_DIR/output"
    mkdir -p "$OUTPUT_DIR"
    
    print_success "目录结构创建完成: $WORK_DIR"
}

# 克隆 strongSwan 源码
clone_strongswan() {
    print_info "克隆 strongSwan 源码..."
    
    if [ -d "strongswan" ]; then
        print_warning "strongswan 目录已存在，跳过克隆"
        cd strongswan
        git pull
    else
        git clone https://github.com/strongswan/strongswan.git
        cd strongswan
    fi
    
    # 切换到稳定版本 (可选)
    # git checkout 5.9.7
    
    print_success "strongSwan 源码获取完成"
}

# 准备 strongSwan 源码
prepare_strongswan() {
    print_info "准备 strongSwan 源码..."
    
    # 运行 autogen.sh 和 configure
    ./autogen.sh
    
    # 配置 strongSwan (用于生成必要的文件)
    ./configure --disable-defaults --enable-shared --disable-static
    
    # 生成 dist 文件
    make dist
    
    print_success "strongSwan 源码准备完成"
}

# 构建 OpenSSL
build_openssl() {
    print_info "构建 OpenSSL for Android..."
    
    # 进入 Android 前端目录
    cd src/frontends/android
    
    # 删除现有的 openssl 目录 (如果存在)
    if [ -d "app/src/main/jni/openssl" ]; then
        rm -rf app/src/main/jni/openssl
    fi
    
    # 运行 OpenSSL 构建脚本
    print_info "运行 OpenSSL 构建脚本..."
    ANDROID_NDK_ROOT="$ANDROID_NDK_ROOT" \
    OPENSSL_SRC="$OPENSSL_SRC" \
    NO_DOCKER=1 \
    ./openssl/build.sh
    
    if [ $? -eq 0 ]; then
        print_success "OpenSSL 构建完成"
    else
        print_error "OpenSSL 构建失败"
        exit 1
    fi
}

# 构建 Android 应用
build_android_app() {
    print_info "构建 Android 应用..."
    
    # 检查 Android SDK
    if [ -z "$ANDROID_SDK_ROOT" ]; then
        print_warning "未设置 ANDROID_SDK_ROOT，尝试使用默认路径"
        if [ -d "$HOME/Android/Sdk" ]; then
            export ANDROID_SDK_ROOT="$HOME/Android/Sdk"
        else
            print_error "请设置 ANDROID_SDK_ROOT 环境变量"
            exit 1
        fi
    fi
    
    # 设置 NDK 路径
    if [ -z "$NDK_DIR" ]; then
        export NDK_DIR="$ANDROID_NDK_ROOT"
    fi
    
    # 创建 local.properties 文件
    cat > local.properties << EOF
ndk.dir=$ANDROID_NDK_ROOT
sdk.dir=$ANDROID_SDK_ROOT
EOF
    
    # 构建应用
    print_info "开始构建 Android 应用..."
    ./gradlew assembleRelease
    
    if [ $? -eq 0 ]; then
        print_success "Android 应用构建完成"
    else
        print_error "Android 应用构建失败"
        exit 1
    fi
}

# 提取 .so 文件
extract_so_files() {
    print_info "提取 .so 文件..."
    
    # 查找生成的 APK 文件
    APK_FILE=$(find app/build/outputs/apk -name "*.apk" | head -1)
    
    if [ -z "$APK_FILE" ]; then
        print_error "未找到生成的 APK 文件"
        exit 1
    fi
    
    print_info "找到 APK 文件: $APK_FILE"
    
    # 创建临时目录
    TEMP_DIR="/tmp/strongswan_extract"
    mkdir -p "$TEMP_DIR"
    
    # 解压 APK
    unzip -q "$APK_FILE" -d "$TEMP_DIR"
    
    # 复制 .so 文件
    if [ -d "$TEMP_DIR/lib" ]; then
        cp -r "$TEMP_DIR/lib"/* "$OUTPUT_DIR/"
        print_success ".so 文件提取完成"
        
        # 显示提取的文件
        print_info "提取的 .so 文件:"
        find "$OUTPUT_DIR" -name "*.so" | while read file; do
            echo "  - $file"
        done
    else
        print_error "APK 中未找到 lib 目录"
    fi
    
    # 清理临时目录
    rm -rf "$TEMP_DIR"
}

# 创建移植说明
create_integration_guide() {
    print_info "创建移植说明文档..."
    
    cat > "$OUTPUT_DIR/README.md" << 'EOF'
# strongSwan Android 库文件

## 文件说明

本目录包含编译好的 strongSwan Android 库文件，可以移植到其他 Android 项目中使用。

## 目录结构

```
output/
├── arm64-v8a/          # ARM 64位架构
├── armeabi-v7a/        # ARM 32位架构
├── x86/                # x86 32位架构
├── x86_64/             # x86 64位架构
└── README.md           # 本说明文件
```

## 主要库文件

- `libstrongswan.so` - strongSwan 核心库
- `libcharon.so` - IKE 守护进程库
- `libipsec.so` - 用户空间 IPsec 实现
- `libandroidbridge.so` - Android 桥接库
- `libcrypto_static.a` - OpenSSL 静态库

## 使用方法

### 1. 复制库文件

将对应架构的库文件复制到你的 Android 项目的 `app/src/main/jniLibs/` 目录下：

```
app/src/main/jniLibs/
├── arm64-v8a/
│   └── libstrongswan.so
├── armeabi-v7a/
│   └── libstrongswan.so
├── x86/
│   └── libstrongswan.so
└── x86_64/
    └── libstrongswan.so
```

### 2. 配置 CMakeLists.txt

在你的 `app/src/main/cpp/CMakeLists.txt` 中添加：

```cmake
# 添加 strongSwan 库
add_library(strongswan SHARED IMPORTED)
set_target_properties(strongswan PROPERTIES
    IMPORTED_LOCATION ${CMAKE_CURRENT_SOURCE_DIR}/../jniLibs/${ANDROID_ABI}/libstrongswan.so)

add_library(charon SHARED IMPORTED)
set_target_properties(charon PROPERTIES
    IMPORTED_LOCATION ${CMAKE_CURRENT_SOURCE_DIR}/../jniLibs/${ANDROID_ABI}/libcharon.so)

add_library(ipsec SHARED IMPORTED)
set_target_properties(ipsec PROPERTIES
    IMPORTED_LOCATION ${CMAKE_CURRENT_SOURCE_DIR}/../jniLibs/${ANDROID_ABI}/libipsec.so)

add_library(androidbridge SHARED IMPORTED)
set_target_properties(androidbridge PROPERTIES
    IMPORTED_LOCATION ${CMAKE_CURRENT_SOURCE_DIR}/../jniLibs/${ANDROID_ABI}/libandroidbridge.so)

# 链接库
target_link_libraries(your_target
    strongswan
    charon
    ipsec
    androidbridge
    crypto
    ssl
    log
    android
)
```

### 3. 添加头文件

将 strongSwan 的头文件复制到你的项目中：

```bash
# 从 strongSwan 源码目录复制头文件
cp -r /path/to/strongswan/src/lib*/*.h your_project/app/src/main/cpp/include/
```

### 4. 配置权限

在 `AndroidManifest.xml` 中添加必要的权限：

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-permission android:name="android.permission.CHANGE_NETWORK_STATE" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
```

## 注意事项

1. 确保你的项目支持 NDK 开发
2. 根据目标设备选择合适的架构
3. 可能需要根据具体需求调整编译选项
4. 建议在真机上测试，模拟器可能不支持某些网络功能

## 技术支持

- strongSwan 官方文档: https://docs.strongswan.org/
- strongSwan GitHub: https://github.com/strongswan/strongswan
- Android NDK 文档: https://developer.android.com/ndk
EOF

    print_success "移植说明文档创建完成: $OUTPUT_DIR/README.md"
}

# 显示构建信息
show_build_info() {
    print_success "构建完成！"
    echo
    print_info "构建信息:"
    echo "  工作目录: $WORK_DIR"
    echo "  输出目录: $OUTPUT_DIR"
    echo "  Android NDK: $ANDROID_NDK_ROOT"
    echo "  OpenSSL 源码: $OPENSSL_SRC"
    echo
    print_info "生成的文件:"
    find "$OUTPUT_DIR" -name "*.so" | while read file; do
        echo "  - $file"
    done
    echo
    print_info "下一步:"
    echo "  1. 查看 $OUTPUT_DIR/README.md 了解如何使用"
    echo "  2. 将 .so 文件复制到你的 Android 项目中"
    echo "  3. 配置 CMakeLists.txt 和权限"
}

# 主函数
main() {
    print_info "开始构建 strongSwan Android 库文件..."
    echo
    
    # 检查环境
    check_environment
    
    # 创建目录
    create_directories
    
    # 克隆源码
    clone_strongswan
    
    # 准备源码
    prepare_strongswan
    
    # 构建 OpenSSL
    build_openssl
    
    # 构建 Android 应用
    build_android_app
    
    # 提取 .so 文件
    extract_so_files
    
    # 创建移植说明
    create_integration_guide
    
    # 显示构建信息
    show_build_info
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
