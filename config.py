import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Настройка логирования для отладки
logging.basicConfig(level=logging.INFO)

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID', 0))
    MODERATION_CHAT_ID = os.getenv('MODERATION_CHAT_ID')  # ID чата/канала для модерации заказов
    
    # Цены за одиночные диски
    PRICE_SINGLE_R13 = int(os.getenv('PRICE_SINGLE_R13', 200))
    PRICE_SINGLE_R14 = int(os.getenv('PRICE_SINGLE_R14', 300))
    PRICE_SINGLE_R15 = int(os.getenv('PRICE_SINGLE_R15', 300))
    PRICE_SINGLE_R16 = int(os.getenv('PRICE_SINGLE_R16', 400))
    PRICE_SINGLE_R17 = int(os.getenv('PRICE_SINGLE_R17', 500))
    PRICE_SINGLE_R18 = int(os.getenv('PRICE_SINGLE_R18', 700))
    PRICE_SINGLE_R19 = int(os.getenv('PRICE_SINGLE_R19', 900))
    PRICE_SINGLE_R20 = int(os.getenv('PRICE_SINGLE_R20', 1100))
    PRICE_SINGLE_R21 = int(os.getenv('PRICE_SINGLE_R21', 1200))
    PRICE_SINGLE_R22 = int(os.getenv('PRICE_SINGLE_R22', 1200))
    PRICE_SINGLE_R23 = int(os.getenv('PRICE_SINGLE_R23', 1300))
    PRICE_SINGLE_R24 = int(os.getenv('PRICE_SINGLE_R24', 1500))
    
    # Цены за комплекты
    PRICE_SET_R13 = int(os.getenv('PRICE_SET_R13', 700))
    PRICE_SET_R14 = int(os.getenv('PRICE_SET_R14', 700))
    PRICE_SET_R15 = int(os.getenv('PRICE_SET_R15', 800))
    PRICE_SET_R16 = int(os.getenv('PRICE_SET_R16', 800))
    PRICE_SET_R17 = int(os.getenv('PRICE_SET_R17', 1000))
    PRICE_SET_R18 = int(os.getenv('PRICE_SET_R18', 1200))
    PRICE_SET_R19 = int(os.getenv('PRICE_SET_R19', 1400))
    PRICE_SET_R20 = int(os.getenv('PRICE_SET_R20', 1600))
    PRICE_SET_R21 = int(os.getenv('PRICE_SET_R21', 1800))
    PRICE_SET_R22 = int(os.getenv('PRICE_SET_R22', 2000))
    PRICE_SET_R23 = int(os.getenv('PRICE_SET_R23', 2200))
    PRICE_SET_R24 = int(os.getenv('PRICE_SET_R24', 2500))
    
    # Доплата за подготовку
    PRICE_PREP_SINGLE = int(os.getenv('PRICE_PREP_SINGLE', 210))  # Подготовка одиночки
    PRICE_PREP_SET = int(os.getenv('PRICE_PREP_SET', 300))        # Подготовка комплекта
    
    # Доплата за алюмохром
    PRICE_ALUMOCHROME_EXTRA = int(os.getenv('PRICE_ALUMOCHROME_EXTRA', 300))
    
    # Цены за новые типы заказов (для маляра)
    PRICE_NAKIDKA = int(os.getenv('PRICE_NAKIDKA', 300))  # Покраска насадок
    PRICE_SUSPENSIA_PAINT = int(os.getenv('PRICE_SUSPENSIA_PAINT', 500))  # Супорт покраска
    PRICE_SUSPENSIA_LOGO = int(os.getenv('PRICE_SUSPENSIA_LOGO', 750))  # Супорт с логотипом
    
    # Цены для пескоструйщика - комплекты
    PRICE_SANDBLASTER_SET_R12 = int(os.getenv('PRICE_SANDBLASTER_SET_R12', 600))
    PRICE_SANDBLASTER_SET_R13 = int(os.getenv('PRICE_SANDBLASTER_SET_R13', 700))
    PRICE_SANDBLASTER_SET_R14 = int(os.getenv('PRICE_SANDBLASTER_SET_R14', 700))
    PRICE_SANDBLASTER_SET_R15 = int(os.getenv('PRICE_SANDBLASTER_SET_R15', 700))
    PRICE_SANDBLASTER_SET_R16 = int(os.getenv('PRICE_SANDBLASTER_SET_R16', 820))
    PRICE_SANDBLASTER_SET_R17 = int(os.getenv('PRICE_SANDBLASTER_SET_R17', 820))
    PRICE_SANDBLASTER_SET_R18 = int(os.getenv('PRICE_SANDBLASTER_SET_R18', 940))
    PRICE_SANDBLASTER_SET_R19 = int(os.getenv('PRICE_SANDBLASTER_SET_R19', 1200))
    PRICE_SANDBLASTER_SET_R20 = int(os.getenv('PRICE_SANDBLASTER_SET_R20', 1200))
    PRICE_SANDBLASTER_SET_R21 = int(os.getenv('PRICE_SANDBLASTER_SET_R21', 1200))
    PRICE_SANDBLASTER_SET_R22 = int(os.getenv('PRICE_SANDBLASTER_SET_R22', 1600))
    PRICE_SANDBLASTER_SET_R23 = int(os.getenv('PRICE_SANDBLASTER_SET_R23', 1800))
    PRICE_SANDBLASTER_SET_R24 = int(os.getenv('PRICE_SANDBLASTER_SET_R24', 2000))
    
    # Цены для пескоструйщика - одиночки
    PRICE_SANDBLASTER_SINGLE_R12 = int(os.getenv('PRICE_SANDBLASTER_SINGLE_R12', 150))
    PRICE_SANDBLASTER_SINGLE_R13 = int(os.getenv('PRICE_SANDBLASTER_SINGLE_R13', 175))
    PRICE_SANDBLASTER_SINGLE_R14 = int(os.getenv('PRICE_SANDBLASTER_SINGLE_R14', 175))
    PRICE_SANDBLASTER_SINGLE_R15 = int(os.getenv('PRICE_SANDBLASTER_SINGLE_R15', 175))
    PRICE_SANDBLASTER_SINGLE_R16 = int(os.getenv('PRICE_SANDBLASTER_SINGLE_R16', 205))
    PRICE_SANDBLASTER_SINGLE_R17 = int(os.getenv('PRICE_SANDBLASTER_SINGLE_R17', 205))
    PRICE_SANDBLASTER_SINGLE_R18 = int(os.getenv('PRICE_SANDBLASTER_SINGLE_R18', 235))
    PRICE_SANDBLASTER_SINGLE_R19 = int(os.getenv('PRICE_SANDBLASTER_SINGLE_R19', 300))
    PRICE_SANDBLASTER_SINGLE_R20 = int(os.getenv('PRICE_SANDBLASTER_SINGLE_R20', 300))
    PRICE_SANDBLASTER_SINGLE_R21 = int(os.getenv('PRICE_SANDBLASTER_SINGLE_R21', 300))
    PRICE_SANDBLASTER_SINGLE_R22 = int(os.getenv('PRICE_SANDBLASTER_SINGLE_R22', 400))
    PRICE_SANDBLASTER_SINGLE_R23 = int(os.getenv('PRICE_SANDBLASTER_SINGLE_R23', 450))
    PRICE_SANDBLASTER_SINGLE_R24 = int(os.getenv('PRICE_SANDBLASTER_SINGLE_R24', 500))
    
    # Цены для пескоструйщика - другие типы
    PRICE_SANDBLASTER_NAKIDKA = int(os.getenv('PRICE_SANDBLASTER_NAKIDKA', 150))  # Насадки
    PRICE_SANDBLASTER_SUSPENSIA = int(os.getenv('PRICE_SANDBLASTER_SUSPENSIA', 305))  # Супорта за штуку
    
    # Цены за напыление для пескоструйщика
    PRICE_SPRAYING_DEEP = int(os.getenv('PRICE_SPRAYING_DEEP', 537))  # Глубокое напыление
    PRICE_SPRAYING_SHALLOW = int(os.getenv('PRICE_SPRAYING_SHALLOW', 237))  # Неглубокое напыление
    
    # Настройки базы данных
    DB_HOST = os.getenv('DB_HOST', 'db')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_NAME = os.getenv('DB_NAME', 'painter_bot')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

config = Config()

# Логируем загруженные цены для отладки
logging.info("=== ЗАГРУЖЕННЫЕ ЦЕНЫ ===")
logging.info(f"PRICE_SINGLE_R13: {config.PRICE_SINGLE_R13}")
logging.info(f"PRICE_SINGLE_R14: {config.PRICE_SINGLE_R14}")
logging.info(f"PRICE_SINGLE_R15: {config.PRICE_SINGLE_R15}")
logging.info(f"PRICE_SINGLE_R16: {config.PRICE_SINGLE_R16}")
logging.info(f"PRICE_SINGLE_R17: {config.PRICE_SINGLE_R17}")
logging.info(f"PRICE_SINGLE_R18: {config.PRICE_SINGLE_R18}")
logging.info(f"PRICE_SINGLE_R19: {config.PRICE_SINGLE_R19}")
logging.info(f"PRICE_SINGLE_R20: {config.PRICE_SINGLE_R20}")
logging.info(f"PRICE_SINGLE_R21: {config.PRICE_SINGLE_R21}")
logging.info(f"PRICE_SINGLE_R22: {config.PRICE_SINGLE_R22}")
logging.info(f"PRICE_SINGLE_R23: {config.PRICE_SINGLE_R23}")
logging.info(f"PRICE_SET_R13: {config.PRICE_SET_R13}")
logging.info(f"PRICE_SET_R14: {config.PRICE_SET_R14}")
logging.info(f"PRICE_SET_R15: {config.PRICE_SET_R15}")
logging.info(f"PRICE_SET_R16: {config.PRICE_SET_R16}")
logging.info(f"PRICE_SET_R17: {config.PRICE_SET_R17}")
logging.info(f"PRICE_SET_R18: {config.PRICE_SET_R18}")
logging.info(f"PRICE_SET_R19: {config.PRICE_SET_R19}")
logging.info(f"PRICE_SET_R20: {config.PRICE_SET_R20}")
logging.info(f"PRICE_SET_R21: {config.PRICE_SET_R21}")
logging.info(f"PRICE_SET_R22: {config.PRICE_SET_R22}")
logging.info(f"PRICE_SET_R23: {config.PRICE_SET_R23}")
logging.info(f"PRICE_PREP_SINGLE: {config.PRICE_PREP_SINGLE}")
logging.info(f"PRICE_PREP_SET: {config.PRICE_PREP_SET}")
logging.info(f"PRICE_ALUMOCHROME_EXTRA: {config.PRICE_ALUMOCHROME_EXTRA}")
logging.info("========================")
