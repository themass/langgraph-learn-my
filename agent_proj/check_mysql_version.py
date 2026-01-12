import os
import pymysql
import sys
from urllib.parse import urlparse, quote_plus
from dotenv import load_dotenv

load_dotenv()

def check_version():
    """
    检查 MySQL 版本和 CTE 支持
    从 .env 文件读取数据库配置
    """
    print("=" * 80)
    print("MySQL 版本检查")
    print("=" * 80)
    
    # 从环境变量读取配置
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", "3306"))
    db_name = os.getenv("DB_NAME")
    
    # 如果没有独立配置，尝试解析 DATABASE_URL
    if not all([db_user, db_password, db_name]):
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
    
    print(f"\n[1] 连接信息:")
    print(f"   主机: {db_host}:{db_port}")
    print(f"   用户: {db_user}")
    print(f"   数据库: {db_name}")
    
    print(f"\n[2] 正在连接...")
    try:
        conn = pymysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
        print("✅ 连接成功")
        
        with conn.cursor() as cursor:
            # 检查版本
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"\n[3] MySQL 版本: {version[0]}")
            
            # 检查 CTE 支持
            print(f"\n[4] 检查 CTE (WITH 子句) 支持...")
            try:
                cursor.execute("WITH cte AS (SELECT 1 as test) SELECT * FROM cte")
                result = cursor.fetchone()
                print(f"✅ CTEs 支持正常 (测试结果: {result[0]})")
            except Exception as e:
                print(f"❌ CTEs 不支持: {e}")
                print("   注意: LangGraph MySQL Checkpointer 需要 MySQL 8.0+")
                
        conn.close()
        
        print("\n" + "=" * 80)
        print("✅ 检查完成")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print("\n💡 常见问题:")
        print("   1. 检查数据库服务是否运行")
        print("   2. 检查用户名、密码是否正确")
        print("   3. 检查防火墙/安全组是否允许访问")
        print("   4. 检查用户是否有远程访问权限")

if __name__ == "__main__":
    check_version()
