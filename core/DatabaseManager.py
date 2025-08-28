import os
import sqlite3
from datetime import datetime

class DatabaseManger:
    DATABASE_PATH = 'JTypewriterDB'

    def __init__(self):
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        return sqlite3.connect(database=DatabaseManger.DATABASE_PATH)
    
    def init_db(self) -> None:
        """初始化数据库和表结构"""

        # 数据库不存在，创建新数据库
        if not os.path.exists(DatabaseManger.DATABASE_PATH):
            conn = self.get_connection()
            cursor = conn.cursor()

            # 创建用户表
            cursor.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    level TEXT DEFAULT 'beginner'
                )
            ''')

            conn.commit()
            conn.close()

        print("数据库加载完毕！")