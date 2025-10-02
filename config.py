import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID', 0))
    
    # Цены за одиночные диски
    PRICE_SINGLE_R15 = int(os.getenv('PRICE_SINGLE_R15', 500))
    PRICE_SINGLE_R16 = int(os.getenv('PRICE_SINGLE_R16', 600))
    PRICE_SINGLE_R17 = int(os.getenv('PRICE_SINGLE_R17', 700))
    
    # Цены за комплекты
    PRICE_SET_R15 = int(os.getenv('PRICE_SET_R15', 1800))
    PRICE_SET_R16 = int(os.getenv('PRICE_SET_R16', 2000))
    PRICE_SET_R17 = int(os.getenv('PRICE_SET_R17', 2200))
    
    # Доплата за алюмохром
    PRICE_ALUMOCHROME_EXTRA = int(os.getenv('PRICE_ALUMOCHROME_EXTRA', 300))
    
    # Настройки базы данных
    DB_HOST = os.getenv('DB_HOST', 'db')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_NAME = os.getenv('DB_NAME', 'painter_bot')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

config = Config()
