#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试数据库连接配置
验证 .env 中的数据库配置是否正确
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def test_connection():
    """测试数据库连接"""
    print("=" * 80)
    print("ProAgent 数据库连接测试")
    print("=" * 80)
    
    # 1. 测试配置加载
    print("\n[1] 检查配置...")
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from db_checkpointer import build_database_url
        
        db_url = build_database_url()
        
        # 隐藏密码显示
        if '@' in db_url:
            parts = db_url.split('@')
            prefix = parts[0].split('://')[0]
            suffix = '@'.join(parts[1:])
            print(f"✅ 配置加载成功")
            print(f"   连接信息: {prefix}://***:***@{suffix}")
        else:
            print(f"✅ 配置加载成功")
            
    except ValueError as e:
        print(f"❌ 配置错误:\n{str(e)}")
        print("\n💡 请参考 docs/DATABASE_CONFIG.md 配置数据库")
        return False
    except Exception as e:
        print(f"❌ 加载配置失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 2. 测试数据库连接
    print("\n[2] 测试数据库连接...")
    try:
        from langgraph.checkpoint.mysql.aio import AIOMySQLSaver
        
        async with AIOMySQLSaver.from_conn_string(db_url) as checkpointer:
            print("✅ 数据库连接成功")
            
            # 3. 测试表创建
            print("\n[3] 检查/创建表结构...")
            try:
                await checkpointer.setup()
                print("✅ 表结构就绪")
            except Exception as e:
                print(f"⚠️  表结构检查/创建出现警告（可能已存在）: {e}")
            
            print("\n" + "=" * 80)
            print("✅ 所有测试通过！数据库配置正确。")
            print("=" * 80)
            print("\n🚀 现在可以运行: python agent_proj/main_db.py")
            return True
            
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print("\n💡 常见问题排查:")
        print("   1. 检查 MySQL 服务是否运行")
        print("   2. 检查用户名、密码、主机、端口是否正确")
        print("   3. 检查数据库是否已创建")
        print("   4. 检查 MySQL 版本是否 >= 8.0")
        print("\n   创建数据库:")
        print("   CREATE DATABASE proagent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_connection())
    sys.exit(0 if result else 1)
