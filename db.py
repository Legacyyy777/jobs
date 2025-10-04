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
        try:
            self.pool = await asyncpg.create_pool(
                host=config.DB_HOST,
                port=config.DB_PORT,
                database=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                min_size=1,
                max_size=10,
                command_timeout=30,
                server_settings={
                    'application_name': 'painter_bot',
                }
            )
        except asyncpg.exceptions.InvalidCatalogNameError:
            raise Exception(f"База данных '{config.DB_NAME}' не существует. Проверьте настройки подключения.")
        except asyncpg.exceptions.ConnectionDoesNotExistError:
            raise Exception(f"Не удается подключиться к серверу базы данных {config.DB_HOST}:{config.DB_PORT}")
        except Exception as e:
            raise Exception(f"Ошибка подключения к базе данных: {e}")

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
                    profession VARCHAR(20) DEFAULT 'painter', -- 'painter' или 'sandblaster'
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица заказов (универсальная для всех профессий)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    order_number VARCHAR(50) UNIQUE NOT NULL,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    set_type VARCHAR(20) NOT NULL, -- 'single', 'set', 'nakidka', 'suspensia'
                    size VARCHAR(10), -- 'R15', 'R16', 'R17' (NULL для насадок и суспортов)
                    alumochrome BOOLEAN DEFAULT FALSE,
                    suspensia_type VARCHAR(20), -- 'paint' или 'logo' (только для суспортов)
                    quantity INTEGER DEFAULT 1, -- количество суспортов
                    spraying_deep INTEGER DEFAULT 0, -- количество глубоких напылений
                    spraying_shallow INTEGER DEFAULT 0, -- количество неглубоких напылений
                    price INTEGER NOT NULL,
                    status VARCHAR(20) DEFAULT 'draft', -- 'draft', 'confirmed', 'rejected'
                    photo_file_id VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Миграция для добавления новых полей
            try:
                # Миграция для таблицы пользователей
                await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS profession VARCHAR(20) DEFAULT 'painter'")
                await conn.execute("UPDATE users SET profession = 'painter' WHERE profession IS NULL")
                
                # Миграция для таблицы заказов
                await conn.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS suspensia_type VARCHAR(20)")
                await conn.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS quantity INTEGER DEFAULT 1")
                await conn.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS spraying_deep INTEGER DEFAULT 0")
                await conn.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS spraying_shallow INTEGER DEFAULT 0")
                await conn.execute("ALTER TABLE orders ALTER COLUMN size DROP NOT NULL")
                
                # Удаляем поле profession из таблицы orders, если оно существует
                try:
                    await conn.execute("ALTER TABLE orders DROP COLUMN IF EXISTS profession")
                except Exception:
                    pass  # Игнорируем ошибку, если колонка не существует
            except Exception as e:
                # Игнорируем ошибки, если колонки уже существуют
                pass
            
            # Индексы для оптимизации
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at)")

    async def get_or_create_user(self, tg_id: int, name: str, profession: str = "painter") -> int:
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
                "INSERT INTO users (tg_id, name, profession) VALUES ($1, $2, $3) RETURNING id",
                tg_id, name, profession
            )
            return user_id
    
    async def update_user_profession(self, tg_id: int, profession: str):
        """Обновляет профессию пользователя"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET profession = $1 WHERE tg_id = $2",
                profession, tg_id
            )
    
    async def get_user_profession(self, tg_id: int) -> str:
        """Получает профессию пользователя"""
        async with self.pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT profession FROM users WHERE tg_id = $1",
                tg_id
            )
            return user['profession'] if user else None

    async def create_order(self, order_number: str, user_id: int, set_type: str, 
                          size: str = None, alumochrome: bool = False, price: int = 0, 
                          photo_file_id: str = None, suspensia_type: str = None, quantity: int = 1,
                          spraying_deep: int = 0, spraying_shallow: int = 0) -> int:
        """Создает новый заказ"""
        async with self.pool.acquire() as conn:
            order_id = await conn.fetchval("""
                INSERT INTO orders (order_number, user_id, set_type, size, alumochrome, price, photo_file_id, suspensia_type, quantity, spraying_deep, spraying_shallow)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11) RETURNING id
            """, order_number, user_id, set_type, size, alumochrome, price, photo_file_id, suspensia_type, quantity, spraying_deep, spraying_shallow)
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

    async def check_order_number_exists(self, order_number: str, user_profession: str = None) -> bool:
        """Проверяет, существует ли заказ с таким номером для определенной профессии"""
        async with self.pool.acquire() as conn:
            if user_profession:
                # Проверяем только среди пользователей с той же профессией
                result = await conn.fetchval("""
                    SELECT EXISTS(SELECT 1 FROM orders o 
                    JOIN users u ON o.user_id = u.id 
                    WHERE o.order_number = $1 AND u.profession = $2)
                """, order_number, user_profession)
            else:
                # Проверяем среди всех заказов (для обратной совместимости)
                result = await conn.fetchval(
                    "SELECT EXISTS(SELECT 1 FROM orders WHERE order_number = $1)", order_number
                )
            return result or False

    async def delete_order_by_number(self, order_number: str) -> bool:
        """Удаляет заказ по номеру"""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM orders WHERE order_number = $1", order_number
            )
            return result.split()[-1] == "1"  # Проверяем, что была удалена 1 запись

    async def get_user_orders(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Получает заказы пользователя"""
        async with self.pool.acquire() as conn:
            orders = await conn.fetch("""
                SELECT o.*, u.profession FROM orders o
                JOIN users u ON o.user_id = u.id
                WHERE o.user_id = $1 
                ORDER BY o.created_at DESC 
                LIMIT $2
            """, user_id, limit)
            return [dict(order) for order in orders]

    async def get_order_by_number(self, order_number: str) -> Optional[Dict[str, Any]]:
        """Получает заказ по номеру"""
        async with self.pool.acquire() as conn:
            order = await conn.fetchrow("""
                SELECT o.*, u.tg_id, u.name as user_name
                FROM orders o
                JOIN users u ON o.user_id = u.id
                WHERE o.order_number = $1
            """, order_number)
            return dict(order) if order else None

    async def update_order_price(self, order_id: int, new_price: int) -> bool:
        """Обновляет цену заказа"""
        async with self.pool.acquire() as conn:
            result = await conn.execute("""
                UPDATE orders 
                SET price = $1, updated_at = CURRENT_TIMESTAMP 
                WHERE id = $2
            """, new_price, order_id)
            return result.split()[-1] == "1"

    async def delete_order_by_id(self, order_id: int) -> bool:
        """Удаляет заказ по ID"""
        async with self.pool.acquire() as conn:
            result = await conn.execute("DELETE FROM orders WHERE id = $1", order_id)
            return result.split()[-1] == "1"

    async def get_user_order_by_id(self, user_id: int, order_id: int) -> Optional[Dict[str, Any]]:
        """Получает заказ пользователя по ID"""
        async with self.pool.acquire() as conn:
            order = await conn.fetchrow("""
                SELECT * FROM orders 
                WHERE id = $1 AND user_id = $2
            """, order_id, user_id)
            return dict(order) if order else None

# Глобальный экземпляр базы данных
db = Database()
