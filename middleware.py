"""
Middleware для обработки недоступности базы данных
"""
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable
import logging

logger = logging.getLogger(__name__)

# Глобальная переменная для отслеживания состояния БД
_db_available = False

class DatabaseMiddleware(BaseMiddleware):
    """Middleware для проверки доступности базы данных"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Проверяет доступность БД перед выполнением handler"""
        
        # Проверяем доступность базы данных
        if not _db_available:
            # Если это сообщение от пользователя, отправляем уведомление
            if hasattr(event, 'message') and event.message:
                try:
                    await event.message.answer(
                        "⚠️ Сервис временно недоступен. База данных не отвечает.\n"
                        "Попробуйте позже или обратитесь к администратору."
                    )
                except Exception as e:
                    logger.error(f"Ошибка отправки уведомления: {e}")
            
            # Логируем попытку использования недоступной БД
            logger.warning("Попытка использования БД при её недоступности")
            return
        
        # Если БД доступна, выполняем handler
        return await handler(event, data)

def set_database_available(status: bool):
    """Устанавливает статус доступности базы данных"""
    global _db_available
    _db_available = status

def is_database_available() -> bool:
    """Проверяет доступность базы данных"""
    return _db_available
