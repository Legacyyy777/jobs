import os
from dotenv import load_dotenv

load_dotenv()

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
    
    # Доплата за подготовку
    PRICE_PREP_SINGLE = int(os.getenv('PRICE_PREP_SINGLE', 210))  # Подготовка одиночки
    PRICE_PREP_SET = int(os.getenv('PRICE_PREP_SET', 300))        # Подготовка комплекта
    
    # Доплата за алюмохром
    PRICE_ALUMOCHROME_EXTRA = int(os.getenv('PRICE_ALUMOCHROME_EXTRA', 300))
    
    # Настройки базы данных
    DB_HOST = os.getenv('DB_HOST', 'db')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_NAME = os.getenv('DB_NAME', 'painter_bot')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

config = Config()
