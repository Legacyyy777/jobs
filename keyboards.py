from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню бота"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🎨 Создать заказ", callback_data="create_order"))
    builder.add(InlineKeyboardButton(text="💰 Заработок за день", callback_data="earnings_day"))
    builder.add(InlineKeyboardButton(text="📊 Заработок за месяц", callback_data="earnings_month"))
    builder.add(InlineKeyboardButton(text="✏️ Редактировать заказы", callback_data="edit_orders"))
    builder.add(InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help"))
    builder.adjust(1)
    return builder.as_markup()

def get_set_type_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора типа заказа"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔹 Один диск", callback_data="set_type_single"))
    builder.add(InlineKeyboardButton(text="🔹 Комплект", callback_data="set_type_set"))
    builder.add(InlineKeyboardButton(text="🔸 Насадки", callback_data="set_type_nakidka"))
    builder.add(InlineKeyboardButton(text="🔸 Супорта", callback_data="set_type_suspensia"))
    builder.add(InlineKeyboardButton(text="🆓 Свободный заказ", callback_data="set_type_free"))
    builder.adjust(2)
    return builder.as_markup()

def get_size_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора размера диска"""
    builder = InlineKeyboardBuilder()
    # Добавляем все размеры
    sizes = ["R12", "R13", "R14", "R15", "R16", "R17", "R18", "R19", "R20", "R21", "R22", "R23", "R24"]
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

def get_admin_order_keyboard(order_number: str, order_id: int = None) -> InlineKeyboardMarkup:
    """Клавиатура для админа для управления заказом"""
    builder = InlineKeyboardBuilder()
    if order_id:
        # Используем ID заказа для точной идентификации
        builder.add(InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"admin_confirm_id_{order_id}"))
        builder.add(InlineKeyboardButton(text="✏️ Исправить", callback_data=f"admin_edit_id_{order_id}"))
        builder.add(InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_reject_id_{order_id}"))
    else:
        # Обратная совместимость - используем номер заказа
        builder.add(InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"admin_confirm_{order_number}"))
        builder.add(InlineKeyboardButton(text="✏️ Исправить", callback_data=f"admin_edit_{order_number}"))
        builder.add(InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_reject_{order_number}"))
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

def get_edit_orders_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для редактирования заказов"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="📋 Мои заказы", callback_data="my_orders"))
    builder.add(InlineKeyboardButton(text="🔍 Найти заказ по номеру", callback_data="find_order"))
    builder.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"))
    builder.adjust(1)
    return builder.as_markup()

def get_my_orders_keyboard(orders: list, page: int = 0, total_count: int = 0) -> InlineKeyboardMarkup:
    """Клавиатура для списка заказов пользователя с пагинацией"""
    builder = InlineKeyboardBuilder()
    
    # Кнопки заказов
    for order in orders:
        builder.add(InlineKeyboardButton(
            text=f"📋 Заказ #{order['order_number']}",
            callback_data=f"order_actions_{order['id']}"
        ))
    
    # Навигация по страницам
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"my_orders_page_{page-1}"))
    if (page + 1) * 5 < total_count:
        nav_buttons.append(InlineKeyboardButton(text="Вперёд ▶️", callback_data=f"my_orders_page_{page+1}"))
    
    if nav_buttons:
        for btn in nav_buttons:
            builder.add(btn)
    
    # Кнопка главного меню
    builder.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"))
    
    # Размещаем: заказы по 1 в ряду, навигацию по 2 в ряду (если есть), главное меню по 1 в ряду
    builder.adjust(1, 2, 1)
    return builder.as_markup()

def get_order_actions_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Клавиатура действий с заказом"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✏️ Изменить статус", callback_data=f"change_status_{order_id}"))
    builder.add(InlineKeyboardButton(text="💰 Изменить цену", callback_data=f"change_price_{order_id}"))
    builder.add(InlineKeyboardButton(text="🗑️ Удалить заказ", callback_data=f"delete_order_{order_id}"))
    builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data="edit_orders"))
    builder.adjust(1)
    return builder.as_markup()

def get_status_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для выбора статуса заказа"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="📝 Черновик", callback_data=f"set_status_{order_id}_draft"))
    builder.add(InlineKeyboardButton(text="✅ Подтвержден", callback_data=f"set_status_{order_id}_confirmed"))
    builder.add(InlineKeyboardButton(text="❌ Отклонен", callback_data=f"set_status_{order_id}_rejected"))
    builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data=f"order_actions_{order_id}"))
    builder.adjust(1)
    return builder.as_markup()

def get_confirm_delete_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения удаления заказа"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"confirm_delete_{order_id}"))
    builder.add(InlineKeyboardButton(text="❌ Отмена", callback_data=f"order_actions_{order_id}"))
    builder.adjust(1)
    return builder.as_markup()

def get_suspensia_type_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора типа супортов"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🎨 Покраска (500₽)", callback_data="suspensia_type_paint"))
    builder.add(InlineKeyboardButton(text="🏷️ С логотипом (750₽)", callback_data="suspensia_type_logo"))
    builder.adjust(1)
    return builder.as_markup()

def get_profession_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора профессии"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🎨 Маляр", callback_data="profession_painter"))
    builder.add(InlineKeyboardButton(text="💨 Пескоструйщик", callback_data="profession_sandblaster"))
    builder.adjust(1)
    return builder.as_markup()

def get_spraying_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора напыления"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Да, было напыление", callback_data="spraying_yes"))
    builder.add(InlineKeyboardButton(text="❌ Нет напыления", callback_data="spraying_no"))
    builder.adjust(1)
    return builder.as_markup()
