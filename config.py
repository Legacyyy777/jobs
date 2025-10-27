import os
import logging
from typing import List
from dotenv import load_dotenv

load_dotenv()

# Настройка логирования для отладки
logging.basicConfig(level=logging.INFO)

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID', 0))
    MODERATION_CHAT_ID = os.getenv('MODERATION_CHAT_ID')  # ID чата/канала для модерации заказов
    PAINTER_TOPIC_ID = int(os.getenv('PAINTER_TOPIC_ID', 0)) if os.getenv('PAINTER_TOPIC_ID') else None  # ID топика для маляра
    SANDBLASTER_TOPIC_ID = int(os.getenv('SANDBLASTER_TOPIC_ID', 0)) if os.getenv('SANDBLASTER_TOPIC_ID') else None  # ID топика для пескоструйщика
    
    # Список модераторов из переменной окружения
    @property
    def MODERATORS(self):
        """Возвращает список ID модераторов из переменной окружения"""
        moderators_str = os.getenv('MODERATORS', '')
        if not moderators_str:
            return []
        try:
            return [int(mod_id.strip()) for mod_id in moderators_str.split(',') if mod_id.strip()]
        except ValueError:
            logging.error(f"Ошибка парсинга MODERATORS: {moderators_str}")
            return []
    
    # Ограничение доступа: список разрешенных user_id сотрудников (через запятую)
    _ALLOWED_USER_IDS_RAW = os.getenv('ALLOWED_USER_IDS', '').strip()
    ALLOWED_USER_IDS: List[int] = (
        [int(x) for x in _ALLOWED_USER_IDS_RAW.split(',') if x.strip().isdigit()]
        if _ALLOWED_USER_IDS_RAW else []
    )
    
    # Цены за одиночные диски
    PRICE_SINGLE_R12 = int(os.getenv('PRICE_SINGLE_R12', 150))
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
    PRICE_SET_R12 = int(os.getenv('PRICE_SET_R12', 600))
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
    PRICE_SUSPENSIA_PAINT = int(os.getenv('PRICE_SUSPENSIA_PAINT', 750))  # Супорт покраска
    PRICE_SUSPENSIA_LOGO = int(os.getenv('PRICE_SUSPENSIA_LOGO', 875))  # Супорт с логотипом
    
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

# Красивое логирование цен
def log_prices():
    logging.info("╔══════════════════════════════════════════════════════════════════════════════════╗")
    logging.info("║                                 💰 ЗАГРУЖЕННЫЕ ЦЕНЫ 💰                           ║")
    logging.info("╠══════════════════════════════════════════════════════════════════════════════════╣")
    
    # Цены для маляра - одиночные диски
    logging.info("║ 🎨 МАЛЯР - ОДИНОЧНЫЕ ДИСКИ:                                                      ║")
    prices_single = [
        ("R12", config.PRICE_SINGLE_R12), ("R13", config.PRICE_SINGLE_R13), ("R14", config.PRICE_SINGLE_R14),
        ("R15", config.PRICE_SINGLE_R15), ("R16", config.PRICE_SINGLE_R16), ("R17", config.PRICE_SINGLE_R17),
        ("R18", config.PRICE_SINGLE_R18), ("R19", config.PRICE_SINGLE_R19), ("R20", config.PRICE_SINGLE_R20),
        ("R21", config.PRICE_SINGLE_R21), ("R22", config.PRICE_SINGLE_R22), ("R23", config.PRICE_SINGLE_R23),
        ("R24", config.PRICE_SINGLE_R24)
    ]
    
    for size, price in prices_single:
        logging.info(f"║   {size}: {price:>4}₽                                                                  ║")
    
    # Цены для маляра - комплекты
    logging.info("║ 🎨 МАЛЯР - КОМПЛЕКТЫ:                                                           ║")
    prices_set = [
        ("R12", config.PRICE_SET_R12), ("R13", config.PRICE_SET_R13), ("R14", config.PRICE_SET_R14),
        ("R15", config.PRICE_SET_R15), ("R16", config.PRICE_SET_R16), ("R17", config.PRICE_SET_R17),
        ("R18", config.PRICE_SET_R18), ("R19", config.PRICE_SET_R19), ("R20", config.PRICE_SET_R20),
        ("R21", config.PRICE_SET_R21), ("R22", config.PRICE_SET_R22), ("R23", config.PRICE_SET_R23),
        ("R24", config.PRICE_SET_R24)
    ]
    
    for size, price in prices_set:
        logging.info(f"║   {size}: {price:>4}₽                                                                  ║")
    
    # Цены для пескоструйщика - одиночные диски
    logging.info("║ 💨 ПЕСКОСТРУЙЩИК - ОДИНОЧНЫЕ ДИСКИ:                                              ║")
    sandblaster_single = [
        ("R12", config.PRICE_SANDBLASTER_SINGLE_R12), ("R13", config.PRICE_SANDBLASTER_SINGLE_R13),
        ("R14", config.PRICE_SANDBLASTER_SINGLE_R14), ("R15", config.PRICE_SANDBLASTER_SINGLE_R15),
        ("R16", config.PRICE_SANDBLASTER_SINGLE_R16), ("R17", config.PRICE_SANDBLASTER_SINGLE_R17),
        ("R18", config.PRICE_SANDBLASTER_SINGLE_R18), ("R19", config.PRICE_SANDBLASTER_SINGLE_R19),
        ("R20", config.PRICE_SANDBLASTER_SINGLE_R20), ("R21", config.PRICE_SANDBLASTER_SINGLE_R21),
        ("R22", config.PRICE_SANDBLASTER_SINGLE_R22), ("R23", config.PRICE_SANDBLASTER_SINGLE_R23),
        ("R24", config.PRICE_SANDBLASTER_SINGLE_R24)
    ]
    
    for size, price in sandblaster_single:
        logging.info(f"║   {size}: {price:>4}₽                                                                  ║")
    
    # Цены для пескоструйщика - комплекты
    logging.info("║ 💨 ПЕСКОСТРУЙЩИК - КОМПЛЕКТЫ:                                                    ║")
    sandblaster_set = [
        ("R12", config.PRICE_SANDBLASTER_SET_R12), ("R13", config.PRICE_SANDBLASTER_SET_R13),
        ("R14", config.PRICE_SANDBLASTER_SET_R14), ("R15", config.PRICE_SANDBLASTER_SET_R15),
        ("R16", config.PRICE_SANDBLASTER_SET_R16), ("R17", config.PRICE_SANDBLASTER_SET_R17),
        ("R18", config.PRICE_SANDBLASTER_SET_R18), ("R19", config.PRICE_SANDBLASTER_SET_R19),
        ("R20", config.PRICE_SANDBLASTER_SET_R20), ("R21", config.PRICE_SANDBLASTER_SET_R21),
        ("R22", config.PRICE_SANDBLASTER_SET_R22), ("R23", config.PRICE_SANDBLASTER_SET_R23),
        ("R24", config.PRICE_SANDBLASTER_SET_R24)
    ]
    
    for size, price in sandblaster_set:
        logging.info(f"║   {size}: {price:>4}₽                                                                  ║")
    
    # Дополнительные услуги
    logging.info("║ 🔧 ДОПОЛНИТЕЛЬНЫЕ УСЛУГИ:                                                         ║")
    logging.info(f"║   Подготовка одиночного диска: {config.PRICE_PREP_SINGLE:>4}₽                                       ║")
    logging.info(f"║   Подготовка комплекта: {config.PRICE_PREP_SET:>4}₽                                           ║")
    logging.info(f"║   Доплата за алюмохром: {config.PRICE_ALUMOCHROME_EXTRA:>4}₽                                        ║")
    
    # Цены для специальных услуг
    logging.info("║ 🎯 СПЕЦИАЛЬНЫЕ УСЛУГИ:                                                          ║")
    logging.info(f"║   Насадки (маляр): {config.PRICE_NAKIDKA:>4}₽                                                ║")
    logging.info(f"║   Супорта покраска (маляр): {config.PRICE_SUSPENSIA_PAINT:>4}₽                                  ║")
    logging.info(f"║   Супорта с логотипом (маляр): {config.PRICE_SUSPENSIA_LOGO:>4}₽                               ║")
    logging.info(f"║   Насадки (пескоструйщик): {config.PRICE_SANDBLASTER_NAKIDKA:>4}₽                              ║")
    logging.info(f"║   Супорта (пескоструйщик): {config.PRICE_SANDBLASTER_SUSPENSIA:>4}₽                            ║")
    logging.info(f"║   Глубокое напыление: {config.PRICE_SPRAYING_DEEP:>4}₽                                         ║")
    logging.info(f"║   Неглубокое напыление: {config.PRICE_SPRAYING_SHALLOW:>4}₽                                    ║")
    
    logging.info("╚══════════════════════════════════════════════════════════════════════════════════╝")

# Вызываем функцию логирования
log_prices()
