import asyncpg
import asyncio
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from config import config

class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def create_pool(self):
        """Создает пул соединений с базой данных"""
        self.pool = await asyncpg.create_pool(
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            min_size=1,
            max_size=10
        )

    async def close_pool(self):
        """Закрывает пул соединений"""
        if self.pool:
            await self.pool.close()

    async def init_tables(self):
        """Создает таблицы в базе данных"""
        async with self.pool.acquire() as conn:
            # Таблица пользователей
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    tg_id BIGINT UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица заказов
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    order_number VARCHAR(50) UNIQUE NOT NULL,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    set_type VARCHAR(20) NOT NULL, -- 'single' или 'set'
                    size VARCHAR(10) NOT NULL, -- 'R15', 'R16', 'R17'
                    alumochrome BOOLEAN DEFAULT FALSE,
                    price INTEGER NOT NULL,
                    status VARCHAR(20) DEFAULT 'draft', -- 'draft', 'confirmed', 'rejected'
                    photo_file_id VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Индексы для оптимизации
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at)")

    async def get_or_create_user(self, tg_id: int, name: str) -> int:
        """Получает или создает пользователя, возвращает user_id"""
        async with self.pool.acquire() as conn:
            # Пытаемся найти существующего пользователя
            user = await conn.fetchrow(
                "SELECT id FROM users WHERE tg_id = $1", tg_id
            )
            
            if user:
                return user['id']
            
            # Создаем нового пользователя
            user_id = await conn.fetchval(
                "INSERT INTO users (tg_id, name) VALUES ($1, $2) RETURNING id",
                tg_id, name
            )
            return user_id

    async def create_order(self, order_number: str, user_id: int, set_type: str, 
                          size: str, alumochrome: bool, price: int, photo_file_id: str) -> int:
        """Создает новый заказ"""
        async with self.pool.acquire() as conn:
            order_id = await conn.fetchval("""
                INSERT INTO orders (order_number, user_id, set_type, size, alumochrome, price, photo_file_id)
                VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id
            """, order_number, user_id, set_type, size, alumochrome, price, photo_file_id)
            return order_id

    async def update_order_status(self, order_id: int, status: str):
        """Обновляет статус заказа"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE orders SET status = $1, updated_at = CURRENT_TIMESTAMP WHERE id = $2",
                status, order_id
            )

    async def get_order_by_id(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Получает заказ по ID"""
        async with self.pool.acquire() as conn:
            order = await conn.fetchrow("""
                SELECT o.*, u.tg_id, u.name as user_name
                FROM orders o
                JOIN users u ON o.user_id = u.id
                WHERE o.id = $1
            """, order_id)
            return dict(order) if order else None

    async def get_user_earnings_today(self, user_id: int) -> int:
        """Получает заработок пользователя за сегодня"""
        today = date.today()
        async with self.pool.acquire() as conn:
            result = await conn.fetchval("""
                SELECT COALESCE(SUM(price), 0)
                FROM orders
                WHERE user_id = $1 AND status = 'confirmed' AND DATE(created_at) = $2
            """, user_id, today)
            return result or 0

    async def get_user_earnings_month(self, user_id: int) -> int:
        """Получает заработок пользователя за текущий месяц"""
        today = date.today()
        first_day_of_month = today.replace(day=1)
        
        async with self.pool.acquire() as conn:
            result = await conn.fetchval("""
                SELECT COALESCE(SUM(price), 0)
                FROM orders
                WHERE user_id = $1 AND status = 'confirmed' AND created_at >= $2
            """, user_id, first_day_of_month)
            return result or 0

    async def get_user_orders_count(self, user_id: int) -> int:
        """Получает количество заказов пользователя"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT COUNT(*) FROM orders WHERE user_id = $1", user_id
            )
            return result or 0

# Глобальный экземпляр базы данных
db = Database()
