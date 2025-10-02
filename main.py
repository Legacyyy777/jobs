import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from db import db
from handlers import order_handlers, admin_handlers

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Основная функция запуска бота"""
    
    # Отладочная информация
    logger.info("=== ОТЛАДКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ ===")
    logger.info(f"BOT_TOKEN: {'ЕСТЬ' if config.BOT_TOKEN else 'НЕТ'}")
    logger.info(f"PRICE_SINGLE_R15: {config.PRICE_SINGLE_R15}")
    logger.info(f"PRICE_SET_R15: {config.PRICE_SET_R15}")
    logger.info(f"PRICE_PREP_SINGLE: {config.PRICE_PREP_SINGLE}")
    logger.info("=====================================")
    
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
    
    try:
        # Подключаемся к базе данных
        logger.info("Подключение к базе данных...")
        await db.create_pool()
        await db.init_tables()
        logger.info("База данных инициализирована")
        
        # Запускаем бота
        logger.info("Запуск бота...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        # Закрываем соединения
        await db.close_pool()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
