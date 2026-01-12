# strongSwan Android 编译工具链

## 项目概述

这是一个完整的 strongSwan Android VPN 客户端编译工具链，用于生成可移植到其他 Android 项目的 .so 库文件。

基于 [strongSwan 官方文档](https://docs.strongswan.org/docs/latest/os/androidVpnClientBuild.html) 和 [GitHub 仓库](https://github.com/strongswan/strongswan/)。

## 文件结构

```
strongswan/
├── build_strongswan_android.sh      # 主编译脚本
├── setup_strongswan_env.sh          # 环境设置脚本
├── test_strongswan_env.sh           # 环境测试脚本
├── quick_start.sh                   # 快速开始脚本
├── STRONGSWAN_BUILD_GUIDE.md        # 详细编译指南
├── PROJECT_SUMMARY.md               # 项目总结
├── android_integration_example/     # Android 集成示例
│   ├── CMakeLists.txt              # CMake 配置文件
│   ├── build.gradle                # Gradle 构建文件
│   ├── AndroidManifest.xml         # Android 清单文件
│   └── src/                        # 源代码目录
│       ├── main.cpp                # C++ 主文件
│       └── StrongSwanNative.java   # Java JNI 接口
└── README.md                        # 本文件
```

## 快速开始

### 1. 一键运行

```bash
cd strongswan
chmod +x quick_start.sh
./quick_start.sh
```

选择 "4) 完整流程" 即可自动完成所有步骤。

### 2. 分步执行

#### 步骤 1: 设置环境

```bash
cd strongswan
chmod +x setup_strongswan_env.sh
./setup_strongswan_env.sh
```

#### 步骤 2: 加载环境变量

```bash
source ~/strongswan_env.sh
```

#### 步骤 3: 测试环境

```bash
chmod +x test_strongswan_env.sh
./test_strongswan_env.sh
```

#### 步骤 4: 编译 strongSwan

```bash
chmod +x build_strongswan_android.sh
./build_strongswan_android.sh
```

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
- Java 8+

## 编译输出

编译完成后，您将获得以下文件：

```
strongswan_build/output/
├── arm64-v8a/                    # ARM 64位架构
│   ├── libstrongswan.so         # strongSwan 核心库
│   ├── libcharon.so             # IKE 守护进程库
│   ├── libipsec.so              # 用户空间 IPsec 实现
│   ├── libandroidbridge.so      # Android 桥接库
│   └── libcrypto_static.a       # OpenSSL 静态库
├── armeabi-v7a/                 # ARM 32位架构
│   └── (相同的库文件)
├── x86/                         # x86 32位架构
│   └── (相同的库文件)
├── x86_64/                      # x86 64位架构
│   └── (相同的库文件)
└── README.md                    # 使用说明
```

## Android 项目集成

### 1. 复制库文件

将编译生成的 .so 文件复制到您的 Android 项目：

```bash
# 创建目录结构
mkdir -p your_android_project/app/src/main/jniLibs

# 复制库文件
cp -r strongswan_build/output/* your_android_project/app/src/main/jniLibs/
```

### 2. 配置 CMakeLists.txt

参考 `android_integration_example/CMakeLists.txt` 文件。

### 3. 添加权限

在 `AndroidManifest.xml` 中添加必要权限：

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-permission android:name="android.permission.CHANGE_NETWORK_STATE" />
<uses-permission android:name="android.permission.BIND_VPN_SERVICE" />
```

### 4. 使用示例

参考 `android_integration_example/` 目录中的示例代码。

## 脚本说明

### build_strongswan_android.sh
主编译脚本，包含以下功能：
- 克隆 strongSwan 源码
- 准备编译环境
- 构建 OpenSSL for Android
- 编译 Android 应用
- 提取 .so 文件
- 生成使用说明

### setup_strongswan_env.sh
环境设置脚本，包含以下功能：
- 安装系统依赖
- 下载 Android NDK r25c
- 下载 OpenSSL 3.1.0
- 下载 Android SDK 命令行工具
- 创建环境配置文件

### test_strongswan_env.sh
环境测试脚本，包含以下功能：
- 检查必要命令
- 验证环境变量
- 测试 Android NDK
- 测试 OpenSSL
- 检查磁盘空间
- 测试网络连接

### quick_start.sh
快速开始脚本，提供交互式菜单：
- 设置编译环境
- 测试编译环境
- 编译 strongSwan
- 完整流程
- 查看使用说明

## 常见问题

### Q: 编译失败，提示找不到 OpenSSL
A: 确保 `OPENSSL_SRC` 环境变量指向正确的 OpenSSL 源码目录

### Q: Android NDK 版本不兼容
A: 建议使用 NDK r25c，其他版本可能存在兼容性问题

### Q: 编译时间过长
A: 这是正常现象，完整编译可能需要 30-60 分钟

### Q: 生成的 .so 文件过大
A: 可以使用 `strip` 命令减小文件大小

### Q: 在 Android 项目中链接失败
A: 确保 CMakeLists.txt 中正确配置了库路径和链接选项

## 技术支持

- [strongSwan 官方文档](https://docs.strongswan.org/)
- [strongSwan GitHub](https://github.com/strongswan/strongswan)
- [Android NDK 文档](https://developer.android.com/ndk)

## 许可证

strongSwan 使用 GPL v2 许可证，请确保您的项目符合相关许可证要求。

## 更新日志

### v1.0.0
- 初始版本
- 支持 Linux 和 macOS
- 支持多架构编译
- 提供完整的集成示例
- 包含自动化脚本和测试工具
