# LangGraph 学习项目

## 项目概述

这是一个 LangGraph 学习项目，包含各种 LangGraph 示例和工具。

## 目录结构

```
learn/
├── testing/                         # 测试和工具目录
│   ├── strongswan/                 # strongSwan Android 编译工具链
│   │   ├── build_strongswan_android.sh      # 主编译脚本
│   │   ├── setup_strongswan_env.sh          # 环境设置脚本
│   │   ├── test_strongswan_env.sh           # 环境测试脚本
│   │   ├── quick_start.sh                   # 快速开始脚本
│   │   ├── STRONGSWAN_BUILD_GUIDE.md        # 详细编译指南
│   │   ├── PROJECT_SUMMARY.md               # 项目总结
│   │   ├── android_integration_example/     # Android 集成示例
│   │   └── README.md                        # strongSwan 说明文档
│   └── (其他测试文件...)
├── (其他 LangGraph 示例文件...)
└── README.md                        # 本文件
```

## strongSwan Android 编译工具链

strongSwan Android 编译工具链已移动到 `testing/strongswan/` 目录下。

### 快速开始

```bash
cd testing/strongswan
chmod +x quick_start.sh
./quick_start.sh
```

详细说明请查看 [strongswan/README.md](strongswan/README.md)。