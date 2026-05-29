import aiosqlite
from typing import Optional
from datetime import datetime


class Database:
    def __init__(self, db_path: str = "./data/posts.db"):
        self.db_path = db_path

    async def init(self):
        """Инициализация базы данных"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS processed_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_channel TEXT NOT NULL,
                    source_message_id INTEGER NOT NULL,
                    target_message_id INTEGER,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'success',
                    error_message TEXT,
                    UNIQUE(source_channel, source_message_id)
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS api_key_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    api_key_index INTEGER NOT NULL,
                    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN DEFAULT TRUE,
                    error_message TEXT
                )
            """)
            
            await db.commit()

    async def is_processed(self, source_channel: str, message_id: int) -> bool:
        """Проверка, был ли пост уже обработан"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT 1 FROM processed_posts WHERE source_channel = ? AND source_message_id = ?",
                (source_channel, message_id)
            ) as cursor:
                result = await cursor.fetchone()
                return result is not None

    async def mark_processed(
        self,
        source_channel: str,
        source_message_id: int,
        target_message_id: Optional[int] = None,
        status: str = "success",
        error_message: Optional[str] = None
    ):
        """Отметить пост как обработанный"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO processed_posts 
                (source_channel, source_message_id, target_message_id, status, error_message)
                VALUES (?, ?, ?, ?, ?)
                """,
                (source_channel, source_message_id, target_message_id, status, error_message)
            )
            await db.commit()

    async def log_api_usage(self, api_key_index: int, success: bool = True, error_message: Optional[str] = None):
        """Логирование использования API ключа"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO api_key_usage (api_key_index, success, error_message) VALUES (?, ?, ?)",
                (api_key_index, success, error_message)
            )
            await db.commit()

    async def get_least_used_key_index(self, total_keys: int) -> int:
        """Получить индекс наименее используемого ключа"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT api_key_index, COUNT(*) as usage_count
                FROM api_key_usage
                WHERE used_at > datetime('now', '-1 hour')
                GROUP BY api_key_index
                ORDER BY usage_count ASC
                LIMIT 1
            """) as cursor:
                result = await cursor.fetchone()
                if result:
                    return result[0]
                # Если нет записей, возвращаем случайный индекс
                import random
                return random.randint(0, total_keys - 1)
