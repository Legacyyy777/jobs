#!/usr/bin/env python3
"""
Скрипт восстановления соединения с базой данных
Используется для диагностики и восстановления соединения с PostgreSQL
"""

import asyncio
import asyncpg
import logging
import sys
from datetime import datetime
from config import config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseRecovery:
    def __init__(self):
        self.pool = None

    async def test_connection(self):
        """Тестирует базовое соединение с PostgreSQL"""
        try:
            logger.info("🔄 Тестирование соединения с PostgreSQL...")
            conn = await asyncpg.connect(
                host=config.DB_HOST,
                port=config.DB_PORT,
                database=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                timeout=10
            )
            
            # Выполняем простой запрос
            result = await conn.fetchval("SELECT version()")
            logger.info(f"✅ Соединение успешно! Версия PostgreSQL: {result}")
            
            await conn.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка соединения: {e}")
            return False

    async def test_pool_connection(self):
        """Тестирует соединение через пул"""
        try:
            logger.info("🔄 Тестирование пула соединений...")
            self.pool = await asyncpg.create_pool(
                host=config.DB_HOST,
                port=config.DB_PORT,
                database=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                min_size=1,
                max_size=5,
                command_timeout=30
            )
            
            async with self.pool.acquire() as conn:
                result = await conn.fetchval("SELECT current_timestamp")
                logger.info(f"✅ Пул соединений работает! Время сервера: {result}")
            
            await self.pool.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка пула соединений: {e}")
            return False

    async def check_database_status(self):
        """Проверяет статус базы данных"""
        try:
            logger.info("🔄 Проверка статуса базы данных...")
            conn = await asyncpg.connect(
                host=config.DB_HOST,
                port=config.DB_PORT,
                database=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                timeout=10
            )
            
            # Проверяем активные соединения
            active_connections = await conn.fetchval(
                "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
            )
            
            # Проверяем заблокированные запросы
            blocked_queries = await conn.fetchval(
                "SELECT count(*) FROM pg_stat_activity WHERE wait_event_type = 'Lock'"
            )
            
            # Проверяем размер базы данных
            db_size = await conn.fetchval(
                "SELECT pg_size_pretty(pg_database_size(current_database()))"
            )
            
            logger.info(f"📊 Статистика базы данных:")
            logger.info(f"   - Активные соединения: {active_connections}")
            logger.info(f"   - Заблокированные запросы: {blocked_queries}")
            logger.info(f"   - Размер базы данных: {db_size}")
            
            await conn.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки статуса: {e}")
            return False

    async def check_tables(self):
        """Проверяет существование и структуру таблиц"""
        try:
            logger.info("🔄 Проверка таблиц...")
            conn = await asyncpg.connect(
                host=config.DB_HOST,
                port=config.DB_PORT,
                database=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                timeout=10
            )
            
            # Проверяем таблицу users
            users_exists = await conn.fetchval(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"
            )
            
            # Проверяем таблицу orders
            orders_exists = await conn.fetchval(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'orders')"
            )
            
            if users_exists:
                users_count = await conn.fetchval("SELECT count(*) FROM users")
                logger.info(f"✅ Таблица users существует, записей: {users_count}")
            else:
                logger.warning("⚠️ Таблица users не существует")
            
            if orders_exists:
                orders_count = await conn.fetchval("SELECT count(*) FROM orders")
                logger.info(f"✅ Таблица orders существует, записей: {orders_count}")
            else:
                logger.warning("⚠️ Таблица orders не существует")
            
            await conn.close()
            return users_exists and orders_exists
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки таблиц: {e}")
            return False

    async def recreate_tables(self):
        """Пересоздает таблицы (ОСТОРОЖНО!)"""
        try:
            logger.warning("⚠️ ВНИМАНИЕ: Пересоздание таблиц приведет к потере данных!")
            response = input("Вы уверены? Введите 'yes' для подтверждения: ")
            
            if response.lower() != 'yes':
                logger.info("❌ Операция отменена")
                return False
            
            logger.info("🔄 Пересоздание таблиц...")
            conn = await asyncpg.connect(
                host=config.DB_HOST,
                port=config.DB_PORT,
                database=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                timeout=30
            )
            
            # Удаляем таблицы если существуют
            await conn.execute("DROP TABLE IF EXISTS orders CASCADE")
            await conn.execute("DROP TABLE IF EXISTS users CASCADE")
            
            # Создаем таблицы заново
            await conn.execute("""
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    tg_id BIGINT UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    profession VARCHAR(20) DEFAULT 'painter',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await conn.execute("""
                CREATE TABLE orders (
                    id SERIAL PRIMARY KEY,
                    order_number VARCHAR(50) NOT NULL,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    set_type VARCHAR(20) NOT NULL,
                    size VARCHAR(10),
                    alumochrome BOOLEAN DEFAULT FALSE,
                    suspensia_type VARCHAR(20),
                    quantity INTEGER DEFAULT 1,
                    spraying_deep INTEGER DEFAULT 0,
                    spraying_shallow INTEGER DEFAULT 0,
                    price INTEGER NOT NULL,
                    status VARCHAR(20) DEFAULT 'draft',
                    photo_file_id VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Создаем индексы
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at)")
            
            logger.info("✅ Таблицы успешно пересозданы")
            await conn.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка пересоздания таблиц: {e}")
            return False

    async def kill_idle_connections(self):
        """Завершает простаивающие соединения"""
        try:
            logger.info("🔄 Завершение простаивающих соединений...")
            conn = await asyncpg.connect(
                host=config.DB_HOST,
                port=config.DB_PORT,
                database=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                timeout=10
            )
            
            # Находим простаивающие соединения (кроме текущего)
            idle_connections = await conn.fetch("""
                SELECT pid, state, query_start, state_change, query
                FROM pg_stat_activity 
                WHERE state = 'idle' 
                AND pid != pg_backend_pid()
                AND state_change < now() - interval '5 minutes'
            """)
            
            if idle_connections:
                logger.info(f"Найдено {len(idle_connections)} простаивающих соединений")
                for conn_info in idle_connections:
                    try:
                        await conn.execute(f"SELECT pg_terminate_backend({conn_info['pid']})")
                        logger.info(f"✅ Завершено соединение PID {conn_info['pid']}")
                    except Exception as e:
                        logger.warning(f"⚠️ Не удалось завершить PID {conn_info['pid']}: {e}")
            else:
                logger.info("✅ Простаивающих соединений не найдено")
            
            await conn.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка завершения соединений: {e}")
            return False

async def main():
    """Основная функция восстановления"""
    recovery = DatabaseRecovery()
    
    logger.info("🚀 Запуск диагностики базы данных")
    logger.info(f"📋 Параметры подключения:")
    logger.info(f"   - Хост: {config.DB_HOST}:{config.DB_PORT}")
    logger.info(f"   - База данных: {config.DB_NAME}")
    logger.info(f"   - Пользователь: {config.DB_USER}")
    logger.info("=" * 60)
    
    # Тестируем базовое соединение
    if not await recovery.test_connection():
        logger.error("❌ Базовое соединение не удалось. Проверьте настройки.")
        return
    
    # Тестируем пул соединений
    if not await recovery.test_pool_connection():
        logger.error("❌ Пул соединений не работает.")
        return
    
    # Проверяем статус базы данных
    await recovery.check_database_status()
    
    # Проверяем таблицы
    tables_ok = await recovery.check_tables()
    
    if not tables_ok:
        logger.warning("⚠️ Проблемы с таблицами обнаружены")
        response = input("Пересоздать таблицы? (yes/no): ")
        if response.lower() == 'yes':
            await recovery.recreate_tables()
    
    # Завершаем простаивающие соединения
    await recovery.kill_idle_connections()
    
    logger.info("✅ Диагностика завершена")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("❌ Операция прервана пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
