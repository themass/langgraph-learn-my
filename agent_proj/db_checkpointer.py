"""
Database Checkpointer Configuration
"""
from langgraph.checkpoint.mysql.aio import AIOMySQLSaver
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
import os
from contextlib import asynccontextmanager
from urllib.parse import quote_plus

def build_database_url():
    """
    构建数据库连接字符串，支持两种方式：
    1. 直接使用 DATABASE_URL（优先）
    2. 从独立的配置项构建（避免密码特殊字符问题）
    
    Returns:
        str: 数据库连接字符串
    """
    # 方式 1: 直接使用完整的 DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url
    
    # 方式 2: 从独立配置项构建（推荐）
    db_driver = os.getenv("DB_DRIVER", "mysql+aiomysql")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME")
    
    if not all([db_user, db_password, db_name]):
        raise ValueError(
            "数据库配置不完整！请在 .env 中配置以下任一方式：\n"
            "方式 1: DATABASE_URL=mysql+aiomysql://user:pass@host:port/dbname\n"
            "方式 2: DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME (密码会自动转义)"
        )
    
    # 自动转义密码中的特殊字符（如 @, :, / 等）
    escaped_password = quote_plus(db_password)
    
    # 构建连接字符串
    database_url = f"{db_driver}://{db_user}:{escaped_password}@{db_host}:{db_port}/{db_name}"
    
    return database_url

@asynccontextmanager
async def get_checkpointer():
    """
    Async context manager for MySQL Checkpointer.
    Usage:
        async with get_checkpointer() as checkpointer:
            graph.compile(checkpointer=checkpointer)
    """
    database_url = build_database_url()
    
    print(f"📊 数据库连接: {database_url.split('@')[0].split('://')[0]}://***:***@{database_url.split('@')[1] if '@' in database_url else 'N/A'}")
    
    # Use the factory method which handles connection creation correctly
    async with AIOMySQLSaver.from_conn_string(database_url) as checkpointer:
        # 确保表结构存在
        try:
            await checkpointer.setup()
        except Exception as e:
            # Table already exists or other benign error
            pass
            
        yield checkpointer
