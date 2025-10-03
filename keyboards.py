from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню бота"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🎨 Создать заказ", callback_data="create_order"))
    builder.add(InlineKeyboardButton(text="💰 Заработок за день", callback_data="earnings_day"))
    builder.add(InlineKeyboardButton(text="📊 Заработок за месяц", callback_data="earnings_month"))
    builder.add(InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help"))
    builder.adjust(1)
    return builder.as_markup()

def get_set_type_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора типа заказа (один диск или комплект)"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔹 Один диск", callback_data="set_type_single"))
    builder.add(InlineKeyboardButton(text="🔹 Комплект", callback_data="set_type_set"))
    builder.adjust(1)
    return builder.as_markup()

def get_size_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора размера диска"""
    builder = InlineKeyboardBuilder()
    # Добавляем все размеры
    sizes = ["R13", "R14", "R15", "R16", "R17", "R18", "R19", "R20", "R21", "R22", "R23"]
    for size in sizes:
        builder.add(InlineKeyboardButton(text=size, callback_data=f"size_{size}"))
    
    # Размещаем по 2 кнопки в ряду для лучшей читаемости
    builder.adjust(2)
    return builder.as_markup()

def get_alumochrome_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора алюмохрома"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Да", callback_data="alumochrome_yes"))
    builder.add(InlineKeyboardButton(text="❌ Нет", callback_data="alumochrome_no"))
    builder.adjust(2)
    return builder.as_markup()

def get_admin_order_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для админа для управления заказом"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"admin_confirm_{order_id}"))
    builder.add(InlineKeyboardButton(text="✏️ Исправить", callback_data=f"admin_edit_{order_id}"))
    builder.add(InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_reject_{order_id}"))
    builder.adjust(1)
    return builder.as_markup()

def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для отмены операции"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"))
    builder.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"))
    builder.adjust(1)
    return builder.as_markup()

def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для возврата в главное меню"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"))
    return builder.as_markup()

def get_order_exists_keyboard(order_number: str) -> InlineKeyboardMarkup:
    """Клавиатура когда заказ с таким номером уже существует"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✏️ Перезаписать заказ", callback_data=f"overwrite_order_{order_number}"))
    builder.add(InlineKeyboardButton(text="🔄 Ввести другой номер", callback_data="change_order_number"))
    builder.add(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"))
    builder.adjust(1)
    return builder.as_markup()

def get_start_keyboard() -> ReplyKeyboardMarkup:
    """Обычная клавиатура (пустая)"""
    builder = ReplyKeyboardBuilder()
    # Убираем кнопку Старт
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)
