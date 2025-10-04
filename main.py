import asyncio
import logging
import signal
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from db import db
from handlers import order_handlers, admin_handlers, edit_handlers
from middleware import DatabaseMiddleware, set_database_available, is_database_available

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Используем функции из middleware для управления состоянием БД

async def health_check_task():
    """Задача для периодической проверки состояния базы данных"""
    while True:
        try:
            await asyncio.sleep(300)  # Проверяем каждые 5 минут
            if not await db.health_check():
                logger.warning("⚠️ База данных недоступна, попытка переподключения...")
                try:
                    await db.reconnect()
                    set_database_available(True)
                    logger.info("✅ База данных восстановлена")
                except Exception as reconnect_error:
                    logger.error(f"❌ Не удалось переподключиться к БД: {reconnect_error}")
                    set_database_available(False)
                    # Если база данных не существует, не пытаемся переподключиться
                    if "не существует" in str(reconnect_error) or "does not exist" in str(reconnect_error):
                        logger.error("❌ База данных не существует. Требуется ручное вмешательство.")
                        await asyncio.sleep(600)  # Ждем 10 минут перед следующей попыткой
            else:
                if not is_database_available():
                    set_database_available(True)
                    logger.info("✅ База данных снова доступна")
        except Exception as e:
            logger.error(f"❌ Ошибка в health check: {e}")
            set_database_available(False)
            await asyncio.sleep(60)  # Ждем минуту при ошибке

async def graceful_shutdown(signum, frame):
    """Обработчик для корректного завершения работы"""
    logger.info("🛑 Получен сигнал завершения, закрываем соединения...")
    await db.close_pool()
    sys.exit(0)

async def main():
    """Основная функция запуска бота"""
    
    # Устанавливаем обработчики сигналов для корректного завершения
    signal.signal(signal.SIGINT, lambda s, f: asyncio.create_task(graceful_shutdown(s, f)))
    signal.signal(signal.SIGTERM, lambda s, f: asyncio.create_task(graceful_shutdown(s, f)))
    
    # Красивое логирование системной информации
    logger.info("╔══════════════════════════════════════════════════════════════════════════════════╗")
    logger.info("║                          🔧 СИСТЕМНАЯ ИНФОРМАЦИЯ 🔧                              ║")
    logger.info("╠══════════════════════════════════════════════════════════════════════════════════╣")
    logger.info(f"║ 🤖 Токен бота: {'✅ НАСТРОЕН' if config.BOT_TOKEN else '❌ ОТСУТСТВУЕТ'}                                                      ║")
    logger.info(f"║ 🗄️  База данных: PostgreSQL                                                      ║")
    logger.info(f"║ 📊 Образец цен: R15 одиночный: {config.PRICE_SINGLE_R15}₽, комплект: {config.PRICE_SET_R15}₽                        ║")
    logger.info(f"║ 🛠️  Подготовка одиночного диска: {config.PRICE_PREP_SINGLE}₽                                                ║")
    logger.info("╚══════════════════════════════════════════════════════════════════════════════════╝")
    
    # Проверяем наличие токена
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN не найден в переменных окружения!")
        return
    
    # Создаем бота и диспетчер
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Добавляем middleware для проверки БД
    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    
    # Регистрируем роутеры
    dp.include_router(order_handlers.router)
    dp.include_router(admin_handlers.router)
    dp.include_router(edit_handlers.router)
    
    # Инициализируем состояние БД как недоступную
    set_database_available(False)
    
    try:
        # Подключаемся к базе данных с повторными попытками
        logger.info("🔄 Подключение к базе данных...")
        max_retries = 5
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                await db.create_pool()
                await db.init_tables()
                set_database_available(True)
                logger.info("✅ База данных успешно инициализирована")
                break
            except Exception as db_error:
                logger.warning(f"⚠️  Попытка {attempt + 1}/{max_retries} подключения к БД неудачна: {db_error}")
                
                # Если это ошибка отсутствия БД, увеличиваем задержку
                if "не существует" in str(db_error) or "does not exist" in str(db_error):
                    retry_delay = 10  # Больше времени для создания БД
                    logger.info("🔄 Обнаружена проблема с базой данных, увеличиваем время ожидания...")
                
                if attempt < max_retries - 1:
                    logger.info(f"⏳ Повторная попытка через {retry_delay} секунд...")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error("❌ Не удалось подключиться к базе данных после всех попыток")
                    logger.warning("⚠️ Бот запускается в режиме без базы данных")
                    logger.info("💡 Попробуйте: docker-compose restart")
                    set_database_available(False)
        
        # Запускаем задачу мониторинга базы данных
        health_task = asyncio.create_task(health_check_task())
        
        # Запускаем бота
        logger.info("🚀 Запуск бота...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при запуске бота: {e}")
    finally:
        # Отменяем задачу мониторинга
        if 'health_task' in locals():
            health_task.cancel()
        # Закрываем соединения
        logger.info("🔌 Закрытие соединений...")
        await db.close_pool()
        await bot.session.close()
        logger.info("✅ Соединения закрыты")

if __name__ == "__main__":
    asyncio.run(main())
