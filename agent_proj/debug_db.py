import asyncio
import aiomysql
import sys
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

async def test_connection():
    """
    测试数据库连接
    从 .env 文件读取数据库配置
    """
    print("=" * 80)
    print("数据库连接调试工具")
    print("=" * 80)
    
    # 从环境变量读取配置
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", "3306"))
    db_name = os.getenv("DB_NAME")
    
    # 如果没有独立配置，尝试解析 DATABASE_URL
    if not all([db_user, db_password, db_name]):
        from urllib.parse import urlparse
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            parsed = urlparse(database_url)
            db_host = parsed.hostname or "localhost"
            db_port = parsed.port or 3306
            db_user = parsed.username
            db_password = parsed.password
            db_name = parsed.path.lstrip('/')
        else:
            print("❌ 数据库配置不完整！")
            print("请在 .env 中配置以下任一方式：")
            print("  方式 1: DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME")
            print("  方式 2: DATABASE_URL")
            return
    
    print(f"\n[1] 连接参数:")
    print(f"   主机: {db_host}:{db_port}")
    print(f"   用户: {db_user}")
    print(f"   密码: {'*' * len(db_password)}")
    print(f"   数据库: {db_name}")
    
    print("\n[2] 测试原始连接 (aiomysql)...")
    try:
        conn = await aiomysql.connect(
            host=db_host, 
            port=db_port, 
            user=db_user, 
            password=db_password, 
            db=db_name,
            autocommit=True
        )
        print("✅ 成功: 原始连接正常！")
        print("   这意味着凭据正确，并且允许远程访问。")
        
        # 检查版本
        async with conn.cursor() as cur:
            await cur.execute("SELECT VERSION()")
            ver = await cur.fetchone()
            print(f"   服务器版本: {ver[0]}")
            
        conn.close()
    except Exception as e:
        print(f"❌ 失败: {e}")
        print("   可能的原因:")
        print("   1. 密码不正确")
        print("   2. 用户不允许从此 IP 访问 (需要 'GRANT ALL ... TO user@%')")
        print("   3. 防火墙/安全组阻止连接")
        return

    print("\n[3] 测试 URL 解析...")
    # 构建标准 URL
    escaped_pwd = quote_plus(db_password)
    url = f"mysql://{db_user}:{escaped_pwd}@{db_host}:{db_port}/{db_name}"
    print(f"   生成的 URL: mysql://{db_user}:***@{db_host}:{db_port}/{db_name}")
    
    # 检查此 URL 是否适用于 langgraph saver
    print("\n[4] 测试 LangGraph Checkpointer...")
    try:
        from langgraph.checkpoint.mysql.aio import AIOMySQLSaver
        async with AIOMySQLSaver.from_conn_string(url) as saver:
            print("✅ 成功: Checkpointer 连接正常！")
            
            # 测试表创建
            try:
                await saver.setup()
                print("✅ 成功: 表结构创建/验证正常！")
            except Exception as e:
                print(f"⚠️  表结构警告: {e}")
                
    except Exception as e:
        print(f"❌ 失败: {e}")
        print("   建议检查:")
        print("   1. MySQL 版本是否 >= 8.0")
        print("   2. 用户是否有建表权限")
        
    print("\n" + "=" * 80)
    print("✅ 测试完成")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_connection())
