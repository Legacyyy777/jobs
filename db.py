import asyncpg
import asyncio
import logging
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
from typing import Optional, List, Dict, Any
from config import config

logger = logging.getLogger(__name__)

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
                command_timeout=60,  # Увеличиваем таймаут команды
                server_settings={
                    'application_name': 'painter_bot',
                    'jit': 'off',  # Отключаем JIT для стабильности
                },
                # Добавляем настройки для стабильности соединения
                setup=self._setup_connection,
                init=self._init_connection,
                # Увеличиваем таймауты
                timeout=30,
                max_queries=50000,
                max_inactive_connection_lifetime=300,  # 5 минут
            )
        except asyncpg.exceptions.InvalidCatalogNameError:
            # Если база данных не существует, пытаемся создать её
            logger.warning(f"База данных '{config.DB_NAME}' не существует. Попытка создания...")
            await self._create_database_if_not_exists()
            # Повторная попытка подключения
            self.pool = await asyncpg.create_pool(
                host=config.DB_HOST,
                port=config.DB_PORT,
                database=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                min_size=1,
                max_size=10,
                command_timeout=60,
                server_settings={
                    'application_name': 'painter_bot',
                    'jit': 'off',
                },
                setup=self._setup_connection,
                init=self._init_connection,
                timeout=30,
                max_queries=50000,
                max_inactive_connection_lifetime=300,
            )
        except asyncpg.exceptions.ConnectionDoesNotExistError:
            raise Exception(f"Не удается подключиться к серверу базы данных {config.DB_HOST}:{config.DB_PORT}")
        except Exception as e:
            raise Exception(f"Ошибка подключения к базе данных: {e}")

    async def _create_database_if_not_exists(self):
        """Создает базу данных если она не существует"""
        max_retries = 5
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                # Подключаемся к базе данных postgres для создания новой БД
                conn = await asyncpg.connect(
                    host=config.DB_HOST,
                    port=config.DB_PORT,
                    database='postgres',  # Подключаемся к стандартной БД
                    user=config.DB_USER,
                    password=config.DB_PASSWORD,
                    timeout=30
                )
                
                # Проверяем, существует ли база данных
                exists = await conn.fetchval(
                    "SELECT 1 FROM pg_database WHERE datname = $1", config.DB_NAME
                )
                
                if not exists:
                    logger.info(f"Создание базы данных '{config.DB_NAME}'...")
                    await conn.execute(f'CREATE DATABASE "{config.DB_NAME}"')
                    logger.info(f"✅ База данных '{config.DB_NAME}' создана успешно")
                else:
                    logger.info(f"✅ База данных '{config.DB_NAME}' уже существует")
                
                await conn.close()
                return  # Успешно создали или нашли БД
                
            except Exception as e:
                logger.warning(f"⚠️ Попытка {attempt + 1}/{max_retries} создания БД неудачна: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"⏳ Повторная попытка через {retry_delay} секунд...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Увеличиваем задержку
                else:
                    logger.error(f"❌ Не удалось создать базу данных после всех попыток")
                    raise Exception(f"Не удалось создать базу данных '{config.DB_NAME}': {e}")

    async def _setup_connection(self, conn):
        """Настройка соединения"""
        # Устанавливаем параметры для стабильности
        await conn.execute("SET statement_timeout = '60s'")
        await conn.execute("SET lock_timeout = '30s'")
        await conn.execute("SET idle_in_transaction_session_timeout = '300s'")

    async def _init_connection(self, conn):
        """Инициализация соединения"""
        # Проверяем соединение
        await conn.fetchval("SELECT 1")

    async def close_pool(self):
        """Закрывает пул соединений"""
        if self.pool:
            await self.pool.close()

    async def health_check(self) -> bool:
        """Проверяет состояние соединения с базой данных"""
        if not self.pool:
            return False
        
        try:
            # Получаем соединение и сразу освобождаем
            conn = await self.pool.acquire()
            try:
                await conn.fetchval("SELECT 1")
                return True
            finally:
                await self.pool.release(conn)
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    async def reconnect(self):
        """Переподключается к базе данных"""
        logger.info("Attempting to reconnect to database...")
        await self.close_pool()
        try:
            await self.create_pool()
            await self.init_tables()
            logger.info("Database reconnected successfully")
        except Exception as e:
            logger.error(f"Failed to reconnect: {e}")
            raise

    async def _execute_with_retry(self, operation, *args, **kwargs):
        """Выполняет операцию с автоматическим переподключением при ошибке"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return await operation(*args, **kwargs)
            except (asyncpg.exceptions.ConnectionDoesNotExistError, 
                    asyncpg.exceptions.TooManyConnectionsError,
                    asyncpg.exceptions.ConnectionFailure) as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Database connection error (attempt {attempt + 1}/{max_retries}): {e}")
                    await self.reconnect()
                    await asyncio.sleep(1)  # Небольшая задержка перед повторной попыткой
                else:
                    raise e
            except Exception as e:
                # Для других типов ошибок не делаем переподключение
                raise e

    async def init_tables(self):
        """Создает таблицы в базе данных"""
        try:
            # Получаем соединение и держим его до конца
            conn = await self.pool.acquire()
            try:
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
                        order_number VARCHAR(50) NOT NULL,
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
                logger.info("🔄 Выполнение миграций базы данных...")
                try:
                    # Миграция для таблицы пользователей
                    await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS profession VARCHAR(20) DEFAULT 'painter'")
                    await conn.execute("UPDATE users SET profession = 'painter' WHERE profession IS NULL")
                    logger.info("✅ Миграция: добавлена колонка profession в таблицу users")
                    
                    # Миграция для таблицы заказов
                    await conn.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS suspensia_type VARCHAR(20)")
                    await conn.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS quantity INTEGER DEFAULT 1")
                    await conn.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS spraying_deep INTEGER DEFAULT 0")
                    await conn.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS spraying_shallow INTEGER DEFAULT 0")
                    await conn.execute("ALTER TABLE orders ALTER COLUMN size DROP NOT NULL")
                    logger.info("✅ Миграция: добавлены колонки для пескоструйщика и супортов")
                    
                    # Миграция для системы напоминаний
                    await conn.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS reminder_sent BOOLEAN DEFAULT FALSE")
                    await conn.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS reminder_message_id BIGINT")
                    logger.info("✅ Миграция: добавлены колонки для системы напоминаний")
                    
                    # Миграция для типа заказа 70/30
                    await conn.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS painter_70_id INTEGER REFERENCES users(id)")
                    await conn.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS painter_30_id INTEGER REFERENCES users(id)")
                    logger.info("✅ Миграция: добавлены колонки для маляров в заказах 70/30")
                    
                    # Удаляем поле profession из таблицы orders, если оно существует
                    try:
                        await conn.execute("ALTER TABLE orders DROP COLUMN IF EXISTS profession")
                    except Exception:
                        pass  # Игнорируем ошибку, если колонка не существует
                    
                    # Удаляем старое ограничение уникальности на order_number, если оно существует
                    try:
                        await conn.execute("ALTER TABLE orders DROP CONSTRAINT IF EXISTS orders_order_number_key")
                    except Exception:
                        pass  # Игнорируем ошибку, если ограничение не существует
                    
                    # Уникальность номеров заказов контролируется на уровне приложения
                    # через проверку в check_order_number_exists с учетом профессии
                    
                    logger.info("✅ Все миграции выполнены успешно")
                except Exception as e:
                    # Игнорируем ошибки, если колонки уже существуют
                    logger.warning(f"⚠️ Предупреждение при выполнении миграций: {e}")
                    pass
                
                # Индексы для оптимизации
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at)")
                
            finally:
                # Освобождаем соединение
                await self.pool.release(conn)
                
        except Exception as e:
            logger.error(f"Ошибка инициализации таблиц: {e}")
            raise Exception(f"Не удалось инициализировать таблицы: {e}")

    async def get_or_create_user(self, tg_id: int, name: str, profession: str = None) -> int:
        """Получает или создает пользователя, возвращает user_id"""
        async with self.pool.acquire() as conn:
            # Пытаемся найти существующего пользователя
            user = await conn.fetchrow(
                "SELECT id, profession FROM users WHERE tg_id = $1", tg_id
            )
            
            if user:
                # Обновляем только имя, профессию только если она передана явно
                if profession:
                    await conn.execute(
                        "UPDATE users SET profession = $1, name = $2 WHERE tg_id = $3",
                        profession, name, tg_id
                    )
                else:
                    await conn.execute(
                        "UPDATE users SET name = $1 WHERE tg_id = $2",
                        name, tg_id
                    )
                return user['id']
            
            # Создаем нового пользователя с профессией по умолчанию
            default_profession = profession or "painter"
            user_id = await conn.fetchval(
                "INSERT INTO users (tg_id, name, profession) VALUES ($1, $2, $3) RETURNING id",
                tg_id, name, default_profession
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
                          spraying_deep: int = 0, spraying_shallow: int = 0, status: str = 'draft',
                          painter_70_id: int = None, painter_30_id: int = None) -> int:
        """Создает новый заказ"""
        async with self.pool.acquire() as conn:
            order_id = await conn.fetchval("""
                INSERT INTO orders (order_number, user_id, set_type, price, status)
                VALUES ($1, $2, $3, $4, $5) RETURNING id
            """, order_number, user_id, set_type, price, status)
            
            # Обновляем заказ с дополнительными данными
            if size or alumochrome is not None or photo_file_id or suspensia_type or quantity != 1 or spraying_deep or spraying_shallow or painter_70_id or painter_30_id:
                update_fields = []
                update_values = []
                param_count = 1
                
                if size:
                    update_fields.append(f"size = ${param_count}")
                    update_values.append(size)
                    param_count += 1
                
                if alumochrome is not None:
                    update_fields.append(f"alumochrome = ${param_count}")
                    update_values.append(alumochrome)
                    param_count += 1
                
                if photo_file_id:
                    update_fields.append(f"photo_file_id = ${param_count}")
                    update_values.append(photo_file_id)
                    param_count += 1
                
                if suspensia_type:
                    update_fields.append(f"suspensia_type = ${param_count}")
                    update_values.append(suspensia_type)
                    param_count += 1
                
                if quantity != 1:
                    update_fields.append(f"quantity = ${param_count}")
                    update_values.append(quantity)
                    param_count += 1
                
                if spraying_deep:
                    update_fields.append(f"spraying_deep = ${param_count}")
                    update_values.append(spraying_deep)
                    param_count += 1
                
                if spraying_shallow:
                    update_fields.append(f"spraying_shallow = ${param_count}")
                    update_values.append(spraying_shallow)
                    param_count += 1
                
                if painter_70_id:
                    update_fields.append(f"painter_70_id = ${param_count}")
                    update_values.append(painter_70_id)
                    param_count += 1
                
                if painter_30_id:
                    update_fields.append(f"painter_30_id = ${param_count}")
                    update_values.append(painter_30_id)
                    param_count += 1
                
                if update_fields:
                    update_values.append(order_id)
                    await conn.execute(f"""
                        UPDATE orders SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ${param_count}
                    """, *update_values)
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
        """Получает заработок пользователя за сегодня (по часовому поясу Уфы)"""
        tz = ZoneInfo("Asia/Yekaterinburg")
        now_local = datetime.now(tz)
        start_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
        end_local = start_local + timedelta(days=1)

        start_utc = start_local.astimezone(ZoneInfo("UTC"))
        end_utc = end_local.astimezone(ZoneInfo("UTC"))

        async with self.pool.acquire() as conn:
            # Получаем заработок от обычных заказов
            regular_earnings = await conn.fetchval("""
                SELECT COALESCE(SUM(price), 0)
                FROM orders
                WHERE user_id = $1
                  AND status = 'confirmed'
                  AND (created_at AT TIME ZONE 'UTC') >= $2
                  AND (created_at AT TIME ZONE 'UTC') <  $3
                  AND set_type NOT LIKE '70_30_%'
            """, user_id, start_utc, end_utc) or 0
            
            # Получаем заработок от заказов 70/30 (70%)
            earnings_70 = await conn.fetchval("""
                SELECT COALESCE(SUM(price * 0.7), 0)
                FROM orders
                WHERE painter_70_id = $1
                  AND status = 'confirmed'
                  AND (created_at AT TIME ZONE 'UTC') >= $2
                  AND (created_at AT TIME ZONE 'UTC') <  $3
                  AND set_type LIKE '70_30_%'
            """, user_id, start_utc, end_utc) or 0
            
            # Получаем заработок от заказов 70/30 (30%)
            earnings_30 = await conn.fetchval("""
                SELECT COALESCE(SUM(price * 0.3), 0)
                FROM orders
                WHERE painter_30_id = $1
                  AND status = 'confirmed'
                  AND (created_at AT TIME ZONE 'UTC') >= $2
                  AND (created_at AT TIME ZONE 'UTC') <  $3
                  AND set_type LIKE '70_30_%'
            """, user_id, start_utc, end_utc) or 0
            
            return int(regular_earnings + earnings_70 + earnings_30)

    async def get_user_earnings_month(self, user_id: int) -> int:
        """Получает заработок пользователя за текущий месяц (по часовому поясу Уфы)"""
        tz = ZoneInfo("Asia/Yekaterinburg")
        now_local = datetime.now(tz)
        start_month_local = now_local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_month_local = (start_month_local + timedelta(days=32)).replace(day=1)

        start_month_utc = start_month_local.astimezone(ZoneInfo("UTC"))
        end_month_utc = end_month_local.astimezone(ZoneInfo("UTC"))

        async with self.pool.acquire() as conn:
            # Получаем заработок от обычных заказов
            regular_earnings = await conn.fetchval("""
                SELECT COALESCE(SUM(price), 0)
                FROM orders
                WHERE user_id = $1
                  AND status = 'confirmed'
                  AND (created_at AT TIME ZONE 'UTC') >= $2
                  AND (created_at AT TIME ZONE 'UTC') <  $3
                  AND set_type NOT LIKE '70_30_%'
            """, user_id, start_month_utc, end_month_utc) or 0
            
            # Получаем заработок от заказов 70/30 (70%)
            earnings_70 = await conn.fetchval("""
                SELECT COALESCE(SUM(price * 0.7), 0)
                FROM orders
                WHERE painter_70_id = $1
                  AND status = 'confirmed'
                  AND (created_at AT TIME ZONE 'UTC') >= $2
                  AND (created_at AT TIME ZONE 'UTC') <  $3
                  AND set_type LIKE '70_30_%'
            """, user_id, start_month_utc, end_month_utc) or 0
            
            # Получаем заработок от заказов 70/30 (30%)
            earnings_30 = await conn.fetchval("""
                SELECT COALESCE(SUM(price * 0.3), 0)
                FROM orders
                WHERE painter_30_id = $1
                  AND status = 'confirmed'
                  AND (created_at AT TIME ZONE 'UTC') >= $2
                  AND (created_at AT TIME ZONE 'UTC') <  $3
                  AND set_type LIKE '70_30_%'
            """, user_id, start_month_utc, end_month_utc) or 0
            
            return int(regular_earnings + earnings_70 + earnings_30)

    async def get_user_avg_earnings_per_day(self, user_id: int) -> float:
        """Получает средний заработок пользователя за день в текущем месяце"""
        tz = ZoneInfo("Asia/Yekaterinburg")
        now_local = datetime.now(tz)
        start_month_local = now_local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_month_local = (start_month_local + timedelta(days=32)).replace(day=1)

        start_month_utc = start_month_local.astimezone(ZoneInfo("UTC"))
        end_month_utc = end_month_local.astimezone(ZoneInfo("UTC"))

        async with self.pool.acquire() as conn:
            # Получаем общий заработок за месяц (обычные заказы + 70/30)
            regular_earnings = await conn.fetchval("""
                SELECT COALESCE(SUM(price), 0)
                FROM orders
                WHERE user_id = $1
                  AND status = 'confirmed'
                  AND (created_at AT TIME ZONE 'UTC') >= $2
                  AND (created_at AT TIME ZONE 'UTC') <  $3
                  AND set_type NOT LIKE '70_30_%'
            """, user_id, start_month_utc, end_month_utc) or 0
            
            earnings_70 = await conn.fetchval("""
                SELECT COALESCE(SUM(price * 0.7), 0)
                FROM orders
                WHERE painter_70_id = $1
                  AND status = 'confirmed'
                  AND (created_at AT TIME ZONE 'UTC') >= $2
                  AND (created_at AT TIME ZONE 'UTC') <  $3
                  AND set_type LIKE '70_30_%'
            """, user_id, start_month_utc, end_month_utc) or 0
            
            earnings_30 = await conn.fetchval("""
                SELECT COALESCE(SUM(price * 0.3), 0)
                FROM orders
                WHERE painter_30_id = $1
                  AND status = 'confirmed'
                  AND (created_at AT TIME ZONE 'UTC') >= $2
                  AND (created_at AT TIME ZONE 'UTC') <  $3
                  AND set_type LIKE '70_30_%'
            """, user_id, start_month_utc, end_month_utc) or 0
            
            total_earnings = regular_earnings + earnings_70 + earnings_30
            
            # Получаем количество уникальных дней с заказами
            days_with_orders = await conn.fetchval("""
                SELECT COUNT(DISTINCT DATE(created_at AT TIME ZONE 'UTC'))
                FROM (
                    SELECT created_at FROM orders WHERE user_id = $1 AND status = 'confirmed' AND (created_at AT TIME ZONE 'UTC') >= $2 AND (created_at AT TIME ZONE 'UTC') < $3 AND set_type NOT LIKE '70_30_%'
                    UNION ALL
                    SELECT created_at FROM orders WHERE painter_70_id = $1 AND status = 'confirmed' AND (created_at AT TIME ZONE 'UTC') >= $2 AND (created_at AT TIME ZONE 'UTC') < $3 AND set_type LIKE '70_30_%'
                    UNION ALL
                    SELECT created_at FROM orders WHERE painter_30_id = $1 AND status = 'confirmed' AND (created_at AT TIME ZONE 'UTC') >= $2 AND (created_at AT TIME ZONE 'UTC') < $3 AND set_type LIKE '70_30_%'
                ) AS all_orders
            """, user_id, start_month_utc, end_month_utc) or 0
            
            # Возвращаем 0 если не было заказов, иначе средний заработок
            if days_with_orders == 0:
                return 0.0
            return total_earnings / days_with_orders

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
    
    async def delete_order_by_number_and_profession(self, order_number: str, profession: str) -> bool:
        """Удаляет заказ по номеру и профессии"""
        async with self.pool.acquire() as conn:
            result = await conn.execute("""
                DELETE FROM orders 
                WHERE order_number = $1 
                AND user_id IN (SELECT id FROM users WHERE profession = $2)
            """, order_number, profession)
            return result.split()[-1] == "1"  # Проверяем, что была удалена 1 запись

    async def get_user_orders(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Получает заказы пользователя (включая заказы 70/30)"""
        async with self.pool.acquire() as conn:
            # Получаем заказы пользователя (обычные + где он участвует в 70/30)
            orders = await conn.fetch("""
                SELECT o.*, u.profession FROM orders o
                JOIN users u ON o.user_id = u.id
                WHERE o.user_id = $1 OR o.painter_70_id = $1 OR o.painter_30_id = $1
                ORDER BY o.created_at DESC 
                LIMIT $2
            """, user_id, limit)
            return [dict(order) for order in orders]

    async def get_order_by_number(self, order_number: str) -> Optional[Dict[str, Any]]:
        """Получает заказ по номеру (возвращает первый найденный)"""
        async with self.pool.acquire() as conn:
            order = await conn.fetchrow("""
                SELECT o.*, u.tg_id, u.name as user_name, u.profession
                FROM orders o
                JOIN users u ON o.user_id = u.id
                WHERE o.order_number = $1
                LIMIT 1
            """, order_number)
            return dict(order) if order else None
    
    async def get_order_by_number_and_profession(self, order_number: str, profession: str) -> Optional[Dict[str, Any]]:
        """Получает заказ по номеру и профессии"""
        async with self.pool.acquire() as conn:
            order = await conn.fetchrow("""
                SELECT o.*, u.tg_id, u.name as user_name, u.profession
                FROM orders o
                JOIN users u ON o.user_id = u.id
                WHERE o.order_number = $1 AND u.profession = $2
            """, order_number, profession)
            return dict(order) if order else None
    
    async def get_user_order_by_number(self, user_id: int, order_number: str) -> Optional[Dict[str, Any]]:
        """Получает заказ пользователя по номеру"""
        async with self.pool.acquire() as conn:
            order = await conn.fetchrow("""
                SELECT o.*, u.profession
                FROM orders o
                JOIN users u ON o.user_id = u.id
                WHERE o.order_number = $1 AND o.user_id = $2
            """, order_number, user_id)
            return dict(order) if order else None
    
    async def get_order_by_id(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Получает заказ по ID"""
        async with self.pool.acquire() as conn:
            order = await conn.fetchrow("""
                SELECT o.*, u.tg_id, u.name as user_name, u.profession
                FROM orders o
                JOIN users u ON o.user_id = u.id
                WHERE o.id = $1
            """, order_id)
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
    
    async def get_user_orders_paginated(self, user_id: int, limit: int = 5, offset: int = 0) -> List[Dict[str, Any]]:
        """Получает заказы пользователя с пагинацией (включая заказы 70/30)"""
        async with self.pool.acquire() as conn:
            orders = await conn.fetch("""
                SELECT o.*, u.profession FROM orders o
                JOIN users u ON o.user_id = u.id
                WHERE o.user_id = $1 OR o.painter_70_id = $1 OR o.painter_30_id = $1
                ORDER BY o.created_at DESC 
                LIMIT $2 OFFSET $3
            """, user_id, limit, offset)
            return [dict(order) for order in orders]

    async def get_user_orders_total_count(self, user_id: int) -> int:
        """Получает общее количество заказов пользователя (включая заказы 70/30)"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT COUNT(*) FROM orders WHERE user_id = $1 OR painter_70_id = $1 OR painter_30_id = $1", user_id
            )
            return result or 0
    
    async def get_unconfirmed_orders_older_than(self, minutes: int) -> List[Dict[str, Any]]:
        """Получает неподтвержденные заказы старше указанного количества минут (только те, которым еще не отправлено напоминание)"""
        async with self.pool.acquire() as conn:
            orders = await conn.fetch("""
                SELECT o.*, u.tg_id, u.name as user_name, u.profession
                FROM orders o
                JOIN users u ON o.user_id = u.id
                WHERE o.status = 'draft'
                AND o.created_at < NOW() - INTERVAL '%s minutes'
                AND (o.reminder_sent IS NULL OR o.reminder_sent = FALSE)
                ORDER BY o.created_at ASC
            """ % minutes)
            return [dict(order) for order in orders]
    
    async def mark_order_as_reminded(self, order_id: int):
        """Помечает заказ как напомненный"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE orders SET reminder_sent = TRUE WHERE id = $1",
                order_id
            )
    
    async def save_reminder_message_id(self, order_id: int, message_id: int):
        """Сохраняет ID сообщения с напоминанием"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE orders SET reminder_message_id = $1 WHERE id = $2",
                message_id, order_id
            )
    
    async def get_reminder_message_id(self, order_id: int) -> Optional[int]:
        """Получает ID сообщения с напоминанием"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT reminder_message_id FROM orders WHERE id = $1",
                order_id
            )
            return result

    async def get_all_painters(self) -> List[Dict[str, Any]]:
        """Получает всех маляров из базы данных"""
        async with self.pool.acquire() as conn:
            painters = await conn.fetch("""
                SELECT tg_id, name, username
                FROM users
                WHERE profession = 'painter'
            """)
            return [dict(painter) for painter in painters]

    async def get_user_name_by_id(self, user_id: int) -> Optional[str]:
        """Получает имя пользователя по ID"""
        async with self.pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT name FROM users WHERE id = $1",
                user_id
            )
            return user['name'] if user else None

# Глобальный экземпляр базы данных
db = Database()
