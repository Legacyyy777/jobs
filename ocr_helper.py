"""
Модуль для распознавания текста с изображений (OCR)
Используется для автоматического извлечения номера заказа из фото
"""

import io
import re
import logging
from typing import Optional

try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logging.warning("⚠️ OCR модули не установлены. Функция распознавания недоступна.")

logger = logging.getLogger(__name__)


def is_ocr_available() -> bool:
    """Проверяет, доступен ли OCR"""
    return OCR_AVAILABLE


async def extract_order_number(photo_bytes: bytes) -> Optional[str]:
    """
    Извлекает номер заказа из фото
    
    Args:
        photo_bytes: Байты изображения
        
    Returns:
        Распознанный номер заказа или None
    """
    if not OCR_AVAILABLE:
        logger.warning("OCR недоступен")
        return None
    
    try:
        # Открываем изображение
        image = Image.open(io.BytesIO(photo_bytes))
        
        # Конвертируем в RGB если нужно
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Распознаём текст (русский + английский)
        text = pytesseract.image_to_string(image, lang='rus+eng', config='--psm 6')
        
        logger.info(f"📝 Распознанный текст: {text[:100]}...")
        
        # Ищем номер заказа по различным паттернам
        patterns = [
            r'№\s*(\d{2,6})',                    # № 123, №123
            r'заказ[:\s]*(\d{2,6})',             # заказ: 123, заказ 123
            r'order[:\s]*(\d{2,6})',             # order: 123
            r'\b([A-ZА-Я]{1,3}-?\d{2,6})\b',     # A-123, ЗК-456
            r'\b(\d{3,6})\b',                    # Просто число 3-6 цифр
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                order_number = match.group(1).strip()
                logger.info(f"✅ Найден номер заказа: {order_number}")
                return order_number
        
        logger.warning("⚠️ Номер заказа не найден в распознанном тексте")
        return None
        
    except Exception as e:
        logger.error(f"❌ Ошибка OCR: {e}")
        return None


async def extract_disk_size(photo_bytes: bytes) -> Optional[str]:
    """
    Извлекает размер диска из фото (R12-R24)
    
    Args:
        photo_bytes: Байты изображения
        
    Returns:
        Распознанный размер или None
    """
    if not OCR_AVAILABLE:
        return None
    
    try:
        image = Image.open(io.BytesIO(photo_bytes))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        text = pytesseract.image_to_string(image, lang='eng', config='--psm 6')
        
        # Ищем размер R12-R24
        pattern = r'\bR(1[2-9]|2[0-4])\b'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            size = f"R{match.group(1)}"
            logger.info(f"✅ Найден размер диска: {size}")
            return size
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Ошибка распознавания размера: {e}")
        return None


def preprocess_image_for_ocr(image: Image.Image) -> Image.Image:
    """
    Предобработка изображения для улучшения качества OCR
    
    Args:
        image: PIL Image объект
        
    Returns:
        Обработанное изображение
    """
    try:
        # Конвертируем в grayscale для лучшего распознавания
        image = image.convert('L')
        
        # Увеличиваем контрастность (опционально)
        # from PIL import ImageEnhance
        # enhancer = ImageEnhance.Contrast(image)
        # image = enhancer.enhance(2)
        
        return image
        
    except Exception as e:
        logger.error(f"Ошибка предобработки: {e}")
        return image

