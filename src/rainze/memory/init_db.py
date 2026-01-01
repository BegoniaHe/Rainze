"""
数据库初始化工具 / Database initialization utility

用于初始化 Rainze 长期记忆数据库。
Initialize Rainze long-term memory database.

Reference:
    - PRD §0.2.3: Layer 3 - Long-term Memory
    - config/database/schema.sql

Author: Rainze Team
Created: 2026-01-01
"""

import sqlite3
from pathlib import Path
from typing import Optional


def initialize_database(
    db_path: str | Path = "./data/memory.db",
    schema_path: str | Path = "./config/database/schema.sql",
    force: bool = False,
) -> None:
    """
    初始化数据库 / Initialize database
    
    Args:
        db_path: 数据库文件路径 / Database file path
        schema_path: Schema SQL 文件路径 / Schema SQL file path
        force: 是否强制重建（会删除现有数据）/ Force rebuild (will delete existing data)
        
    Raises:
        FileNotFoundError: Schema 文件不存在时 / When schema file not found
        sqlite3.Error: 数据库操作失败时 / When database operation fails
    """
    db_path = Path(db_path)
    schema_path = Path(schema_path)
    
    # 检查 schema 文件是否存在 / Check if schema file exists
    if not schema_path.exists():
        raise FileNotFoundError(
            f"Schema file not found / Schema 文件不存在: {schema_path}"
        )
    
    # 如果强制重建，删除现有数据库 / If force rebuild, delete existing database
    if force and db_path.exists():
        print(f"Force rebuild enabled, deleting existing database / 强制重建，删除现有数据库: {db_path}")
        db_path.unlink()
    
    # 确保数据目录存在 / Ensure data directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 读取 schema / Read schema
    with open(schema_path, encoding="utf-8") as f:
        schema_sql = f.read()
    
    # 执行 schema / Execute schema
    try:
        conn = sqlite3.connect(str(db_path))
        conn.executescript(schema_sql)
        conn.commit()
        conn.close()
        
        print(f"✅ Database initialized successfully / 数据库初始化成功: {db_path}")
        
    except sqlite3.Error as e:
        raise sqlite3.Error(f"Failed to initialize database / 数据库初始化失败: {e}") from e


def verify_database(db_path: str | Path = "./data/memory.db") -> bool:
    """
    验证数据库结构 / Verify database structure
    
    Args:
        db_path: 数据库文件路径 / Database file path
        
    Returns:
        是否验证成功 / Whether verification succeeded
    """
    db_path = Path(db_path)
    
    if not db_path.exists():
        print(f"❌ Database not found / 数据库文件不存在: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 检查必要的表是否存在 / Check if required tables exist
        required_tables = [
            "episodes",
            "user_preferences",
            "behavior_patterns",
            "relations",
            "pending_vectorization",
            "memory_metadata",
        ]
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = {row[0] for row in cursor.fetchall()}
        
        missing_tables = set(required_tables) - existing_tables
        
        if missing_tables:
            print(f"❌ Missing tables / 缺少表: {missing_tables}")
            conn.close()
            return False
        
        # 检查元数据 / Check metadata
        cursor.execute("SELECT value FROM memory_metadata WHERE key='schema_version'")
        result = cursor.fetchone()
        
        if result:
            schema_version = result[0]
            print(f"✅ Database verified / 数据库验证成功 (Schema version: {schema_version})")
        else:
            print("⚠️ Database exists but metadata is incomplete / 数据库存在但元数据不完整")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database verification failed / 数据库验证失败: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    # 命令行参数 / Command line arguments
    force_rebuild = "--force" in sys.argv
    
    try:
        # 初始化数据库 / Initialize database
        initialize_database(force=force_rebuild)
        
        # 验证数据库 / Verify database
        verify_database()
        
    except Exception as e:
        print(f"❌ Error / 错误: {e}")
        sys.exit(1)
