import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, PhotoSize
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from handlers.fsm import OrderStates
from keyboards import (
    get_main_menu_keyboard,
    get_set_type_keyboard, 
    get_size_keyboard, 
    get_alumochrome_keyboard,
    get_cancel_keyboard,
    get_back_to_menu_keyboard,
    get_start_keyboard,
    get_order_exists_keyboard
)
from config import config
from db import db

router = Router()

def calculate_price(set_type: str, size: str, alumochrome: bool) -> int:
    """Рассчитывает цену заказа"""
    base_price = 0
    
    # Логируем для отладки
    logging.info(f"Расчет цены: set_type={set_type}, size={size}, alumochrome={alumochrome}")
    
    # Базовая цена в зависимости от типа и размера
    if set_type == "single":
        if size == "R13":
            base_price = config.PRICE_SINGLE_R13
        elif size == "R14":
            base_price = config.PRICE_SINGLE_R14
        elif size == "R15":
            base_price = config.PRICE_SINGLE_R15
        elif size == "R16":
            base_price = config.PRICE_SINGLE_R16
        elif size == "R17":
            base_price = config.PRICE_SINGLE_R17
        elif size == "R18":
            base_price = config.PRICE_SINGLE_R18
        elif size == "R19":
            base_price = config.PRICE_SINGLE_R19
        elif size == "R20":
            base_price = config.PRICE_SINGLE_R20
        elif size == "R21":
            base_price = config.PRICE_SINGLE_R21
        elif size == "R22":
            base_price = config.PRICE_SINGLE_R22
        elif size == "R23":
            base_price = config.PRICE_SINGLE_R23
    else:  # set
        if size == "R13":
            base_price = config.PRICE_SET_R13
        elif size == "R14":
            base_price = config.PRICE_SET_R14
        elif size == "R15":
            base_price = config.PRICE_SET_R15
        elif size == "R16":
            base_price = config.PRICE_SET_R16
        elif size == "R17":
            base_price = config.PRICE_SET_R17
        elif size == "R18":
            base_price = config.PRICE_SET_R18
        elif size == "R19":
            base_price = config.PRICE_SET_R19
        elif size == "R20":
            base_price = config.PRICE_SET_R20
        elif size == "R21":
            base_price = config.PRICE_SET_R21
        elif size == "R22":
            base_price = config.PRICE_SET_R22
        elif size == "R23":
            base_price = config.PRICE_SET_R23
    
    # Добавляем доплату за подготовку
    if set_type == "single":
        base_price += config.PRICE_PREP_SINGLE
    else:
        base_price += config.PRICE_PREP_SET
    
    # Добавляем доплату за алюмохром
    if alumochrome:
        base_price += config.PRICE_ALUMOCHROME_EXTRA
    
    logging.info(f"Итоговая цена: {base_price} руб.")
    return base_price

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    # Игнорируем сообщения из чата модерации
    if str(message.chat.id) == str(config.MODERATION_CHAT_ID):
        return
    
    await state.clear()
    
    # Регистрируем пользователя в базе данных
    user_id = await db.get_or_create_user(
        message.from_user.id, 
        message.from_user.full_name or message.from_user.username or "Unknown"
    )
    
    await message.answer(
        "🎨 <b>Добро пожаловать в бот для маляров!</b>\n\n"
        "Выберите действие:",
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard()
    )

@router.callback_query(F.data == "main_menu")
async def show_main_menu(callback: CallbackQuery, state: FSMContext):
    """Показать главное меню"""
    await state.clear()
    
    await callback.message.edit_text(
        "🎨 <b>Главное меню</b>\n\n"
        "Выберите действие:",
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "create_order")
async def start_create_order(callback: CallbackQuery, state: FSMContext):
    """Начать создание заказа"""
    await callback.message.edit_text(
        "📸 <b>Создание заказа</b>\n\n"
        "Отправьте фото диска(ов), который нужно покрасить:",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )
    
    await state.set_state(OrderStates.waiting_for_photo)
    await callback.answer()

@router.callback_query(F.data == "earnings_day")
async def show_earnings_day(callback: CallbackQuery):
    """Показать заработок за сегодня"""
    user_id = await db.get_or_create_user(
        callback.from_user.id, 
        callback.from_user.full_name or callback.from_user.username or "Unknown"
    )
    
    earnings = await db.get_user_earnings_today(user_id)
    
    await callback.message.edit_text(
        f"💰 <b>Заработок за сегодня:</b> {earnings:,} руб.",
        parse_mode="HTML",
        reply_markup=get_back_to_menu_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "earnings_month")
async def show_earnings_month(callback: CallbackQuery):
    """Показать заработок за месяц"""
    user_id = await db.get_or_create_user(
        callback.from_user.id, 
        callback.from_user.full_name or callback.from_user.username or "Unknown"
    )
    
    earnings = await db.get_user_earnings_month(user_id)
    
    await callback.message.edit_text(
        f"💰 <b>Заработок за текущий месяц:</b> {earnings:,} руб.",
        parse_mode="HTML",
        reply_markup=get_back_to_menu_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "help")
async def show_help(callback: CallbackQuery):
    """Показать справку"""
    help_text = (
        "ℹ️ <b>Справка по боту</b>\n\n"
        "🎨 <b>Создание заказа:</b>\n"
        "1. Нажмите 'Создать заказ'\n"
        "2. Отправьте фото диска(ов)\n"
        "3. Введите номер заказа\n"
        "4. Выберите тип (один диск/комплект)\n"
        "5. Выберите размер диска\n"
        "6. Укажите нужен ли алюмохром\n\n"
        "💰 <b>Статистика:</b>\n"
        "• Заработок за день - сумма за сегодня\n"
        "• Заработок за месяц - сумма за текущий месяц\n\n"
        "📋 <b>Статусы заказов:</b>\n"
        "• Черновик - заказ создан, ожидает подтверждения\n"
        "• Подтвержден - заказ принят, сумма засчитана\n"
        "• Отклонен - заказ не принят\n\n"
        "❓ <b>Проблемы?</b>\n"
        "Обратитесь к администратору"
    )
    
    await callback.message.edit_text(
        help_text,
        parse_mode="HTML",
        reply_markup=get_back_to_menu_keyboard()
    )
    await callback.answer()

@router.message(StateFilter(OrderStates.waiting_for_photo), F.photo)
async def process_photo(message: Message, state: FSMContext):
    """Обработка фото от пользователя"""
    # Сохраняем file_id самого большого фото
    photo = max(message.photo, key=lambda x: x.file_size)
    
    await state.update_data(photo_file_id=photo.file_id)
    
    await message.answer(
        "📸 <b>Фото получено!</b>\n\n"
        "Теперь введите номер заказа:",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )
    
    await state.set_state(OrderStates.waiting_for_order_number)

@router.message(StateFilter(OrderStates.waiting_for_photo))
async def process_non_photo(message: Message):
    """Обработка не-фото в состоянии ожидания фото"""
    await message.answer(
        "❌ Пожалуйста, отправьте фото диска(ов) для покраски.",
        reply_markup=get_cancel_keyboard()
    )


@router.message(StateFilter(OrderStates.waiting_for_order_number))
async def process_order_number(message: Message, state: FSMContext):
    """Обработка номера заказа"""
    order_number = message.text.strip()
    
    if not order_number:
        await message.answer("❌ Номер заказа не может быть пустым. Попробуйте еще раз:")
        return
    
    # Проверяем, не существует ли уже такой номер заказа
    if await db.check_order_number_exists(order_number):
        await message.answer(
            f"⚠️ <b>Заказ с номером '{order_number}' уже существует!</b>\n\n"
            f"Что вы хотите сделать?",
            parse_mode="HTML",
            reply_markup=get_order_exists_keyboard(order_number)
        )
        return
    
    await state.update_data(order_number=order_number)
    
    await message.answer(
        "📋 <b>Номер заказа:</b> {}\n\n"
        "Выберите тип заказа:".format(order_number),
        parse_mode="HTML",
        reply_markup=get_set_type_keyboard()
    )
    
    await state.set_state(OrderStates.waiting_for_set_type)

@router.callback_query(F.data.startswith("set_type_"), StateFilter(OrderStates.waiting_for_set_type))
async def process_set_type(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора типа заказа"""
    set_type = callback.data.split("_")[2]  # single или set
    
    await state.update_data(set_type=set_type)
    
    set_type_text = "один диск" if set_type == "single" else "комплект"
    
    await callback.message.edit_text(
        f"📋 <b>Тип заказа:</b> {set_type_text}\n\n"
        "Выберите размер диска:",
        parse_mode="HTML",
        reply_markup=get_size_keyboard()
    )
    
    await state.set_state(OrderStates.waiting_for_size)

@router.callback_query(F.data.startswith("size_"), StateFilter(OrderStates.waiting_for_size))
async def process_size(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора размера диска"""
    size = callback.data.split("_")[1]  # R15, R16, etc.
    
    logging.info(f"Выбран размер диска: {size}")
    
    await state.update_data(size=size)
    
    await callback.message.edit_text(
        f"📏 <b>Размер диска:</b> {size}\n\n"
        "Нужен ли алюмохром?",
        parse_mode="HTML",
        reply_markup=get_alumochrome_keyboard()
    )
    
    await state.set_state(OrderStates.waiting_for_alumochrome)
    await callback.answer()

@router.callback_query(F.data.startswith("alumochrome_"), StateFilter(OrderStates.waiting_for_alumochrome))
async def process_alumochrome(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора алюмохрома"""
    alumochrome = callback.data.split("_")[1] == "yes"
    
    # Получаем все данные заказа
    data = await state.get_data()
    set_type = data["set_type"]
    size = data["size"]
    
    # Рассчитываем цену
    price = calculate_price(set_type, size, alumochrome)
    
    # Сохраняем данные
    await state.update_data(alumochrome=alumochrome, price=price)
    
    # Получаем все данные заказа
    data = await state.get_data()
    
    # Создаем заказ в базе данных
    user_id = await db.get_or_create_user(
        callback.from_user.id,
        callback.from_user.full_name or callback.from_user.username or "Unknown"
    )
    
    # Проверяем, не существует ли уже такой номер заказа (дополнительная проверка)
    if await db.check_order_number_exists(data["order_number"]):
        await callback.message.edit_text(
            f"⚠️ <b>Заказ с номером '{data['order_number']}' уже существует!</b>\n\n"
            f"Что вы хотите сделать?",
            parse_mode="HTML",
            reply_markup=get_order_exists_keyboard(data["order_number"])
        )
        await callback.answer("❌ Номер заказа уже существует")
        return
    
    try:
        order_id = await db.create_order(
            order_number=data["order_number"],
            user_id=user_id,
            set_type=set_type,
            size=size,
            alumochrome=alumochrome,
            price=price,
            photo_file_id=data["photo_file_id"]
        )
        
        # Отправляем уведомление в чат модерации
        order_data = {
            "order_number": data["order_number"],
            "set_type": set_type,
            "size": size,
            "alumochrome": alumochrome,
            "price": price,
            "photo_file_id": data["photo_file_id"]
        }
        await send_admin_notification(callback.bot, order_id, order_data, callback.from_user.username or callback.from_user.full_name)
        
        # Формируем текст подтверждения
        set_type_text = "один диск" if set_type == "single" else "комплект"
        alumochrome_text = "Да" if alumochrome else "Нет"
        
        await callback.message.edit_text(
            f"✅ <b>Заказ сформирован!</b>\n\n"
            f"📋 <b>Номер заказа:</b> {data['order_number']}\n"
            f"🔹 <b>Тип:</b> {set_type_text}\n"
            f"📏 <b>Размер:</b> {size}\n"
            f"✨ <b>Алюмохром:</b> {alumochrome_text}\n"
            f"💰 <b>Цена:</b> {price:,} руб.\n\n"
            f"Заказ отправлен на рассмотрение администратору.",
            parse_mode="HTML",
            reply_markup=get_back_to_menu_keyboard()
        )
        
    except Exception as e:
        logging.error(f"Ошибка создания заказа: {e}")
        await callback.message.edit_text(
            f"❌ <b>Ошибка создания заказа!</b>\n\n"
            f"Заказ с номером '{data['order_number']}' уже существует.\n"
            f"Пожалуйста, используйте другой номер заказа.",
            parse_mode="HTML",
            reply_markup=get_back_to_menu_keyboard()
        )
        await callback.answer("❌ Ошибка: номер заказа уже существует")
        return
    
    await state.set_state(OrderStates.order_confirmed)

@router.callback_query(F.data.startswith("overwrite_order_"))
async def process_overwrite_order(callback: CallbackQuery, state: FSMContext):
    """Обработка перезаписи заказа"""
    order_number = callback.data.split("_", 2)[2]  # Получаем номер заказа
    
    # Удаляем существующий заказ
    deleted = await db.delete_order_by_number(order_number)
    
    if deleted:
        # Сохраняем номер заказа в состояние
        await state.update_data(order_number=order_number)
        
        await callback.message.edit_text(
            f"✅ <b>Старый заказ удален!</b>\n\n"
            f"📋 <b>Номер заказа:</b> {order_number}\n\n"
            f"Выберите тип заказа:",
            parse_mode="HTML",
            reply_markup=get_set_type_keyboard()
        )
        
        await state.set_state(OrderStates.waiting_for_set_type)
        await callback.answer("✅ Старый заказ удален, продолжаем создание нового")
    else:
        await callback.message.edit_text(
            "❌ <b>Ошибка удаления заказа!</b>\n\n"
            "Попробуйте еще раз или введите другой номер заказа.",
            parse_mode="HTML",
            reply_markup=get_cancel_keyboard()
        )
        await callback.answer("❌ Ошибка удаления заказа")

@router.callback_query(F.data == "change_order_number")
async def process_change_order_number(callback: CallbackQuery, state: FSMContext):
    """Обработка смены номера заказа"""
    await callback.message.edit_text(
        "📝 <b>Введите новый номер заказа:</b>",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )
    
    await state.set_state(OrderStates.waiting_for_order_number)
    await callback.answer("Введите новый номер заказа")

@router.callback_query(F.data == "cancel")
async def process_cancel(callback: CallbackQuery, state: FSMContext):
    """Обработка отмены заказа"""
    await state.clear()
    await callback.message.edit_text(
        "❌ <b>Заказ отменен</b>\n\n"
        "Выберите действие:",
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()

async def send_admin_notification(bot, order_id: int, order_data: dict, username: str):
    """Отправляет уведомление в чат модерации о новом заказе"""
    if not config.MODERATION_CHAT_ID:
        logging.warning("MODERATION_CHAT_ID не настроен, уведомление не отправлено")
        return
    
    set_type_text = "один диск" if order_data.get("set_type") == "single" else "комплект"
    alumochrome_text = "Да" if order_data.get("alumochrome", False) else "Нет"
    
    text = (
        f"🆕 <b>Новый заказ #{order_id}</b>\n\n"
        f"👤 <b>Исполнитель:</b> @{username}\n"
        f"📋 <b>Номер заказа:</b> {order_data.get('order_number', 'Не указан')}\n"
        f"🔹 <b>Тип:</b> {set_type_text}\n"
        f"📏 <b>Размер:</b> {order_data.get('size', 'Не указан')}\n"
        f"✨ <b>Алюмохром:</b> {alumochrome_text}\n"
        f"💰 <b>Цена:</b> {order_data.get('price', 0):,} руб."
    )
    
    try:
        from keyboards import get_admin_order_keyboard
        await bot.send_photo(
            chat_id=config.MODERATION_CHAT_ID,
            photo=order_data["photo_file_id"],
            caption=text,
            parse_mode="HTML",
            reply_markup=get_admin_order_keyboard(order_id)
        )
    except Exception as e:
        logging.error(f"Ошибка отправки уведомления в чат модерации: {e}")


@router.message()
async def handle_any_message(message: Message, state: FSMContext):
    """Обработчик для всех остальных сообщений"""
    # Игнорируем сообщения из чата модерации
    if str(message.chat.id) == str(config.MODERATION_CHAT_ID):
        return
    
    # Если пользователь не в процессе создания заказа, показываем главное меню
    current_state = await state.get_state()
    if current_state is None:
        # Регистрируем пользователя в базе данных
        user_id = await db.get_or_create_user(
            message.from_user.id, 
            message.from_user.full_name or message.from_user.username or "Unknown"
        )
        
        await message.answer(
            "🎨 <b>Добро пожаловать в бот для маляров!</b>\n\n"
            "Выберите действие:",
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        # Если пользователь в процессе создания заказа, но отправил что-то не то
        await message.answer(
            "❌ Неверный формат сообщения. Используйте кнопки для навигации.",
            reply_markup=get_cancel_keyboard()
        )
