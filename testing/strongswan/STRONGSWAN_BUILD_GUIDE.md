# strongSwan Android 编译完整指南

## 概述

本指南将帮助您编译 strongSwan Android VPN 客户端的 .so 文件，以便移植到其他 Android 项目中。

基于 [strongSwan 官方文档](https://docs.strongswan.org/docs/latest/os/androidVpnClientBuild.html) 和 [GitHub 仓库](https://github.com/strongswan/strongswan/)。

## 系统要求

### 操作系统
- Linux (Ubuntu 18.04+, CentOS 7+)
- macOS (10.15+)

### 硬件要求
- 至少 4GB RAM
- 至少 5GB 可用磁盘空间
- 稳定的网络连接

### 软件依赖
- Git
- Make
- Autoconf
- Automake
- Libtool
- pkg-config
- CMake
- Ninja
- Python 3
- Java 8+ (用于 Android 构建)

## 快速开始

### 1. 环境设置

运行环境设置脚本：

```bash
chmod +x setup_strongswan_env.sh
./setup_strongswan_env.sh
```

这个脚本会：
- 安装必要的依赖包
- 下载 Android NDK r25c
- 下载 OpenSSL 3.1.0
- 下载 Android SDK 命令行工具
- 创建环境配置文件

### 2. 加载环境变量

```bash
source ~/strongswan_env.sh
```

### 3. 开始编译

```bash
chmod +x build_strongswan_android.sh
./build_strongswan_android.sh
```

## 详细步骤

### 步骤 1: 环境准备

#### 手动设置环境变量

如果您想手动设置环境，需要以下环境变量：

```bash
# Android NDK 路径
export ANDROID_NDK_ROOT=/path/to/android-ndk-r25c

# OpenSSL 源码路径
export OPENSSL_SRC=/path/to/openssl-3.1.0

# Android SDK 路径 (可选)
export ANDROID_SDK_ROOT=/path/to/Android/Sdk
```

#### 下载必要工具

1. **Android NDK r25c**
   ```bash
   # Linux
   wget https://dl.google.com/android/repository/android-ndk-r25c-linux.zip
   unzip android-ndk-r25c-linux.zip
   
   # macOS
   wget https://dl.google.com/android/repository/android-ndk-r25c-darwin.zip
   unzip android-ndk-r25c-darwin.zip
   ```

2. **OpenSSL 3.1.0**
   ```bash
   wget https://www.openssl.org/source/openssl-3.1.0.tar.gz
   tar -xzf openssl-3.1.0.tar.gz
   ```

### 步骤 2: 获取 strongSwan 源码

```bash
git clone https://github.com/strongswan/strongswan.git
cd strongswan
```

### 步骤 3: 准备源码

```bash
# 生成配置文件
./autogen.sh

# 配置并生成 dist 文件
./configure --disable-defaults --enable-shared --disable-static
make dist
```

### 步骤 4: 构建 OpenSSL

```bash
cd src/frontends/android

# 删除现有的 openssl 目录
rm -rf app/src/main/jni/openssl

# 运行 OpenSSL 构建脚本
ANDROID_NDK_ROOT="$ANDROID_NDK_ROOT" \
OPENSSL_SRC="$OPENSSL_SRC" \
NO_DOCKER=1 \
./openssl/build.sh
```

### 步骤 5: 构建 Android 应用

```bash
# 创建 local.properties 文件
cat > local.properties << EOF
ndk.dir=$ANDROID_NDK_ROOT
sdk.dir=$ANDROID_SDK_ROOT
EOF

# 构建应用
./gradlew assembleRelease
```

### 步骤 6: 提取 .so 文件

```bash
# 查找生成的 APK
APK_FILE=$(find app/build/outputs/apk -name "*.apk" | head -1)

# 解压 APK 并提取 .so 文件
unzip -q "$APK_FILE" -d /tmp/strongswan_extract
cp -r /tmp/strongswan_extract/lib/* ./output/
```

## 编译选项说明

### strongSwan 配置选项

```bash
./configure \
    --disable-defaults \          # 禁用默认配置
    --enable-shared \             # 启用共享库
    --disable-static \            # 禁用静态库
    --enable-android \            # 启用 Android 支持
    --with-android-sdk=$ANDROID_SDK_ROOT \
    --with-android-ndk=$ANDROID_NDK_ROOT
```

### 支持的架构

- `arm64-v8a` - ARM 64位
- `armeabi-v7a` - ARM 32位
- `x86` - x86 32位
- `x86_64` - x86 64位

## 输出文件说明

编译完成后，您将获得以下文件：

```
output/
├── arm64-v8a/
│   ├── libstrongswan.so      # strongSwan 核心库
│   ├── libcharon.so          # IKE 守护进程库
│   ├── libipsec.so           # 用户空间 IPsec 实现
│   └── libandroidbridge.so   # Android 桥接库
├── armeabi-v7a/
│   └── (相同的库文件)
├── x86/
│   └── (相同的库文件)
├── x86_64/
│   └── (相同的库文件)
└── README.md                  # 使用说明
```

## 移植到其他项目

### 1. 复制库文件

将对应架构的库文件复制到您的 Android 项目：

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

```cmake
# 添加 strongSwan 库
add_library(strongswan SHARED IMPORTED)
set_target_properties(strongswan PROPERTIES
    IMPORTED_LOCATION ${CMAKE_CURRENT_SOURCE_DIR}/../jniLibs/${ANDROID_ABI}/libstrongswan.so)

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

### 3. 添加权限

在 `AndroidManifest.xml` 中添加：

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-permission android:name="android.permission.CHANGE_NETWORK_STATE" />
```

## 常见问题

### Q: 编译失败，提示找不到 OpenSSL
A: 确保 `OPENSSL_SRC` 环境变量指向正确的 OpenSSL 源码目录

### Q: Android NDK 版本不兼容
A: 建议使用 NDK r25c，其他版本可能存在兼容性问题

### Q: 编译时间过长
A: 这是正常现象，完整编译可能需要 30-60 分钟

### Q: 生成的 .so 文件过大
A: 可以使用 `strip` 命令减小文件大小：
```bash
strip libstrongswan.so
```

## 技术支持

- [strongSwan 官方文档](https://docs.strongswan.org/)
- [strongSwan GitHub](https://github.com/strongswan/strongswan)
- [Android NDK 文档](https://developer.android.com/ndk)

## 许可证

strongSwan 使用 GPL v2 许可证，请确保您的项目符合相关许可证要求。
