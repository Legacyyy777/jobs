import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from db import db
from handlers import order_handlers, admin_handlers, edit_handlers

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Основная функция запуска бота"""
    
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
    
    # Регистрируем роутеры
    dp.include_router(order_handlers.router)
    dp.include_router(admin_handlers.router)
    dp.include_router(edit_handlers.router)
    
    try:
        # Подключаемся к базе данных с повторными попытками
        logger.info("🔄 Подключение к базе данных...")
        max_retries = 5
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                await db.create_pool()
                await db.init_tables()
                logger.info("✅ База данных успешно инициализирована")
                break
            except Exception as db_error:
                logger.warning(f"⚠️  Попытка {attempt + 1}/{max_retries} подключения к БД неудачна: {db_error}")
                if attempt < max_retries - 1:
                    logger.info(f"⏳ Повторная попытка через {retry_delay} секунд...")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error("❌ Не удалось подключиться к базе данных после всех попыток")
                    raise db_error
        
        # Запускаем бота
        logger.info("🚀 Запуск бота...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при запуске бота: {e}")
    finally:
        # Закрываем соединения
        logger.info("🔌 Закрытие соединений...")
        await db.close_pool()
        await bot.session.close()
        logger.info("✅ Соединения закрыты")

if __name__ == "__main__":
    asyncio.run(main())
