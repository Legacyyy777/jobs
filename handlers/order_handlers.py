import logging
import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, PhotoSize, InlineKeyboardMarkup
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from handlers.fsm import OrderStates
from keyboards import (
    get_main_menu_keyboard,
    get_set_type_keyboard, 
    get_size_keyboard, 
    get_alumochrome_keyboard,
    get_suspensia_type_keyboard,
    get_cancel_keyboard,
    get_back_to_menu_keyboard,
    get_start_keyboard,
    get_order_exists_keyboard
)
from config import config
from db import db

router = Router()

async def safe_edit_message(callback: CallbackQuery, text: str, keyboard: InlineKeyboardMarkup = None, parse_mode: str = "HTML"):
    """Безопасное редактирование сообщения с проверкой на изменение содержимого"""
    # Проверяем, отличается ли новый текст от текущего
    current_text = callback.message.text or ""
    current_markup = callback.message.reply_markup
    
    # Сравниваем тексты (убираем HTML теги для сравнения)
    current_text_clean = re.sub(r'<[^>]+>', '', current_text).strip()
    new_text_clean = re.sub(r'<[^>]+>', '', text).strip()
    
    # Если текст или клавиатура отличаются, редактируем сообщение
    if current_text_clean != new_text_clean or current_markup != keyboard:
        try:
            await callback.message.edit_text(
                text,
                parse_mode=parse_mode,
                reply_markup=keyboard
            )
        except Exception as e:
            # Если не удалось отредактировать (например, сообщение не изменилось),
            # просто отвечаем на callback без ошибки
            logging.warning(f"Failed to edit message: {e}")
    # Если содержимое не изменилось, ничего не делаем

def calculate_price(set_type: str, size: str = None, alumochrome: bool = False, suspensia_type: str = None, quantity: int = 1) -> int:
    """Рассчитывает цену заказа"""
    base_price = 0
    
    # Логируем для отладки
    logging.info(f"Расчет цены: set_type={set_type}, size={size}, alumochrome={alumochrome}, suspensia_type={suspensia_type}, quantity={quantity}")
    
    # Обработка новых типов заказов
    if set_type == "nakidka":
        base_price = config.PRICE_NAKIDKA
        logging.info(f"Цена за насадки: {base_price} руб.")
        return base_price
    
    elif set_type == "suspensia":
        if suspensia_type == "paint":
            base_price = config.PRICE_SUSPENSIA_PAINT
        elif suspensia_type == "logo":
            base_price = config.PRICE_SUSPENSIA_LOGO
        
        # Умножаем на количество
        total_price = base_price * quantity
        logging.info(f"Цена за суспорты: {base_price} руб. × {quantity} шт. = {total_price} руб.")
        return total_price
    
    # Обработка дисков (старая логика)
    elif set_type == "single":
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
        elif size == "R24":
            base_price = config.PRICE_SINGLE_R24
        
        # Добавляем доплату за подготовку
        base_price += config.PRICE_PREP_SINGLE
        
    elif set_type == "set":
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
        elif size == "R24":
            base_price = config.PRICE_SET_R24
        
        # Добавляем доплату за подготовку
        base_price += config.PRICE_PREP_SET
    
    # Добавляем доплату за алюмохром (только для дисков)
    if alumochrome and set_type in ["single", "set"]:
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
    
    text = "🎨 <b>Главное меню</b>\n\nВыберите действие:"
    keyboard = get_main_menu_keyboard()
    
    await safe_edit_message(callback, text, keyboard)
    await callback.answer()


@router.callback_query(F.data == "create_order")
async def start_create_order(callback: CallbackQuery, state: FSMContext):
    """Начать создание заказа"""
    text = "📸 <b>Создание заказа</b>\n\nОтправьте фото диска(ов), который нужно покрасить:"
    keyboard = get_cancel_keyboard()
    
    await safe_edit_message(callback, text, keyboard)
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
    
    text = f"💰 <b>Заработок за сегодня:</b> {earnings:,} руб."
    keyboard = get_back_to_menu_keyboard()
    
    await safe_edit_message(callback, text, keyboard)
    await callback.answer()

@router.callback_query(F.data == "earnings_month")
async def show_earnings_month(callback: CallbackQuery):
    """Показать заработок за месяц"""
    user_id = await db.get_or_create_user(
        callback.from_user.id,
        callback.from_user.full_name or callback.from_user.username or "Unknown"
    )
    
    earnings = await db.get_user_earnings_month(user_id)
    
    text = f"💰 <b>Заработок за текущий месяц:</b> {earnings:,} руб."
    keyboard = get_back_to_menu_keyboard()
    
    await safe_edit_message(callback, text, keyboard)
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
    
    keyboard = get_back_to_menu_keyboard()
    
    await safe_edit_message(callback, help_text, keyboard)
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
    if not message.text:
        await message.answer("❌ Номер заказа не может быть пустым. Попробуйте еще раз:")
        return
    
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
    set_type = callback.data.split("_")[2]  # single, set, nakidka, suspensia
    
    await state.update_data(set_type=set_type)
    
    if set_type == "nakidka":
        # Для насадок рассчитываем цену и создаем заказ
        data = await state.get_data()
        price = calculate_price("nakidka")
        await state.update_data(price=price)
        
        # Создаем заказ
        await create_order_from_data(callback, state)
        return
        
    elif set_type == "suspensia":
        # Для супортов выбираем тип (покраска или с логотипом)
        text = "🔸 <b>Супорта</b>\n\nВыберите тип:"
        keyboard = get_suspensia_type_keyboard()
        
        await safe_edit_message(callback, text, keyboard)
        await state.set_state(OrderStates.waiting_for_suspensia_type)
        await callback.answer()
        return
        
    else:
        # Для дисков (single/set) выбираем размер
        set_type_text = "один диск" if set_type == "single" else "комплект"
        
        text = f"📋 <b>Тип заказа:</b> {set_type_text}\n\nВыберите размер диска:"
        keyboard = get_size_keyboard()
        
        await safe_edit_message(callback, text, keyboard)
        await state.set_state(OrderStates.waiting_for_size)
        await callback.answer()

@router.callback_query(F.data.startswith("size_"), StateFilter(OrderStates.waiting_for_size))
async def process_size(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора размера диска"""
    size = callback.data.split("_")[1]  # R15, R16, etc.
    
    logging.info(f"Выбран размер диска: {size}")
    
    await state.update_data(size=size)
    
    text = f"📏 <b>Размер диска:</b> {size}\n\nНужен ли алюмохром?"
    keyboard = get_alumochrome_keyboard()
    
    await safe_edit_message(callback, text, keyboard)
    
    await state.set_state(OrderStates.waiting_for_alumochrome)
    await callback.answer()

@router.callback_query(F.data.startswith("suspensia_type_"), StateFilter(OrderStates.waiting_for_suspensia_type))
async def process_suspensia_type(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора типа супортов"""
    suspensia_type = callback.data.split("_")[2]  # paint или logo
    
    await state.update_data(suspensia_type=suspensia_type)
    
    text = "🔸 <b>Супорта</b>\n\nВведите количество штук:"
    keyboard = get_cancel_keyboard()
    
    await safe_edit_message(callback, text, keyboard)
    await state.set_state(OrderStates.waiting_for_suspensia_quantity)
    await callback.answer()

@router.message(StateFilter(OrderStates.waiting_for_suspensia_quantity))
async def process_suspensia_quantity(message: Message, state: FSMContext):
    """Обработка количества супортов"""
    if not message.text:
        await message.answer("❌ Количество не может быть пустым. Попробуйте еще раз:")
        return
    
    try:
        quantity = int(message.text.strip())
        
        if quantity <= 0:
            await message.answer("❌ Количество должно быть больше 0. Попробуйте еще раз:")
            return
        
        if quantity > 100:
            await message.answer("❌ Количество не может быть больше 100. Попробуйте еще раз:")
            return
        
        await state.update_data(quantity=quantity)
        
        # Рассчитываем цену и сохраняем
        data = await state.get_data()
        suspensia_type = data["suspensia_type"]
        price = calculate_price(
            set_type="suspensia",
            suspensia_type=suspensia_type,
            quantity=quantity
        )
        await state.update_data(price=price)
        
        # Создаем заказ
        await create_order_from_message_data(message, state)
        
    except ValueError:
        await message.answer("❌ Неверный формат количества. Введите число:")
        return

async def create_order_from_message_data(message: Message, state: FSMContext):
    """Создает заказ из данных состояния для сообщений"""
    data = await state.get_data()
    
    # Создаем заказ в базе данных
    user_id = await db.get_or_create_user(
        message.from_user.id,
        message.from_user.full_name or message.from_user.username or "Unknown"
    )
    
    # Проверяем, не существует ли уже такой номер заказа
    if await db.check_order_number_exists(data["order_number"]):
        await message.answer(
            f"⚠️ <b>Заказ с номером '{data['order_number']}' уже существует!</b>\n\nЧто вы хотите сделать?",
            parse_mode="HTML",
            reply_markup=get_order_exists_keyboard(data["order_number"])
        )
        return
    
    try:
        order_id = await db.create_order(
            order_number=data["order_number"],
            user_id=user_id,
            set_type=data["set_type"],
            size=data.get("size"),
            alumochrome=data.get("alumochrome", False),
            price=data["price"],
            photo_file_id=data["photo_file_id"],
            suspensia_type=data.get("suspensia_type"),
            quantity=data.get("quantity", 1)
        )
        
        # Отправляем уведомление в чат модерации
        order_data = {
            "order_number": data["order_number"],
            "set_type": data["set_type"],
            "size": data.get("size"),
            "alumochrome": data.get("alumochrome", False),
            "suspensia_type": data.get("suspensia_type"),
            "quantity": data.get("quantity", 1),
            "price": data["price"],
            "photo_file_id": data["photo_file_id"]
        }
        await send_admin_notification(message.bot, data["order_number"], order_data, message.from_user.username or message.from_user.full_name)
        
        # Формируем текст подтверждения
        set_type_text = get_set_type_text(data["set_type"], data)
        price = data["price"]
        
        text = (f"✅ <b>Заказ сформирован!</b>\n\n"
                f"📋 <b>Номер заказа:</b> {data['order_number']}\n"
                f"🔹 <b>Тип:</b> {set_type_text}\n"
                f"💰 <b>Цена:</b> {price:,} руб.\n\n"
                f"Заказ отправлен на рассмотрение администратору.")
        
        await message.answer(text, parse_mode="HTML", reply_markup=get_back_to_menu_keyboard())
        
    except Exception as e:
        logging.error(f"Ошибка создания заказа: {e}")
        await message.answer(
            f"❌ <b>Ошибка создания заказа!</b>\n\n"
            f"Заказ с номером '{data['order_number']}' уже существует.\n"
            f"Пожалуйста, используйте другой номер заказа.",
            parse_mode="HTML",
            reply_markup=get_back_to_menu_keyboard()
        )
        return
    
    await state.set_state(OrderStates.order_confirmed)

def get_set_type_text(set_type: str, data: dict) -> str:
    """Возвращает читаемый текст типа заказа"""
    if set_type == "single":
        return "один диск"
    elif set_type == "set":
        return "комплект"
    elif set_type == "nakidka":
        return "насадки"
    elif set_type == "suspensia":
        suspensia_type = data.get("suspensia_type")
        quantity = data.get("quantity", 1)
        if suspensia_type == "paint":
            return f"супорта покраска ({quantity} шт.)"
        elif suspensia_type == "logo":
            return f"супорта с логотипом ({quantity} шт.)"
        else:
            return f"супорта ({quantity} шт.)"
    else:
        return set_type

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
    
    # Создаем заказ
    await create_order_from_data(callback, state)

async def create_order_from_data(callback: CallbackQuery, state: FSMContext):
    """Создает заказ из данных состояния"""
    data = await state.get_data()
    
    # Создаем заказ в базе данных
    user_id = await db.get_or_create_user(
        callback.from_user.id,
        callback.from_user.full_name or callback.from_user.username or "Unknown"
    )
    
    # Проверяем, не существует ли уже такой номер заказа
    if await db.check_order_number_exists(data["order_number"]):
        text = f"⚠️ <b>Заказ с номером '{data['order_number']}' уже существует!</b>\n\nЧто вы хотите сделать?"
        keyboard = get_order_exists_keyboard(data["order_number"])
        
        await safe_edit_message(callback, text, keyboard)
        await callback.answer("❌ Номер заказа уже существует")
        return
    
    try:
        order_id = await db.create_order(
            order_number=data["order_number"],
            user_id=user_id,
            set_type=data["set_type"],
            size=data.get("size"),
            alumochrome=data.get("alumochrome", False),
            price=data["price"],
            photo_file_id=data["photo_file_id"],
            suspensia_type=data.get("suspensia_type"),
            quantity=data.get("quantity", 1)
        )
        
        # Отправляем уведомление в чат модерации
        order_data = {
            "order_number": data["order_number"],
            "set_type": data["set_type"],
            "size": data.get("size"),
            "alumochrome": data.get("alumochrome", False),
            "suspensia_type": data.get("suspensia_type"),
            "quantity": data.get("quantity", 1),
            "price": data["price"],
            "photo_file_id": data["photo_file_id"]
        }
        await send_admin_notification(callback.bot, data["order_number"], order_data, callback.from_user.username or callback.from_user.full_name)
        
        # Формируем текст подтверждения
        set_type_text = get_set_type_text(data["set_type"], data)
        price = data["price"]
        
        text = (f"✅ <b>Заказ сформирован!</b>\n\n"
                f"📋 <b>Номер заказа:</b> {data['order_number']}\n"
                f"🔹 <b>Тип:</b> {set_type_text}\n"
                f"💰 <b>Цена:</b> {price:,} руб.\n\n"
                f"Заказ отправлен на рассмотрение администратору.")
        
        await safe_edit_message(callback, text, get_back_to_menu_keyboard())
        
    except Exception as e:
        logging.error(f"Ошибка создания заказа: {e}")
        text = (f"❌ <b>Ошибка создания заказа!</b>\n\n"
                f"Заказ с номером '{data['order_number']}' уже существует.\n"
                f"Пожалуйста, используйте другой номер заказа.")
        
        await safe_edit_message(callback, text, get_back_to_menu_keyboard())
        await callback.answer("❌ Ошибка: номер заказа уже существует")
        return
    
    await state.set_state(OrderStates.order_confirmed)
    await callback.answer("✅ Заказ создан")

@router.callback_query(F.data.startswith("overwrite_order_"))
async def process_overwrite_order(callback: CallbackQuery, state: FSMContext):
    """Обработка перезаписи заказа"""
    order_number = callback.data.split("_", 2)[2]  # Получаем номер заказа
    
    # Удаляем существующий заказ
    deleted = await db.delete_order_by_number(order_number)
    
    if deleted:
        # Сохраняем номер заказа в состояние
        await state.update_data(order_number=order_number)
        
        text = (f"✅ <b>Старый заказ удален!</b>\n\n"
                f"📋 <b>Номер заказа:</b> {order_number}\n\n"
                f"Выберите тип заказа:")
        keyboard = get_set_type_keyboard()
        
        await safe_edit_message(callback, text, keyboard)
        
        await state.set_state(OrderStates.waiting_for_set_type)
        await callback.answer("✅ Старый заказ удален, продолжаем создание нового")
    else:
        text = "❌ <b>Ошибка удаления заказа!</b>\n\nПопробуйте еще раз или введите другой номер заказа."
        keyboard = get_cancel_keyboard()
        
        await safe_edit_message(callback, text, keyboard)
        await callback.answer("❌ Ошибка удаления заказа")

@router.callback_query(F.data == "change_order_number")
async def process_change_order_number(callback: CallbackQuery, state: FSMContext):
    """Обработка смены номера заказа"""
    text = "📝 <b>Введите новый номер заказа:</b>"
    keyboard = get_cancel_keyboard()
    
    await safe_edit_message(callback, text, keyboard)
    
    await state.set_state(OrderStates.waiting_for_order_number)
    await callback.answer("Введите новый номер заказа")

@router.callback_query(F.data == "cancel")
async def process_cancel(callback: CallbackQuery, state: FSMContext):
    """Обработка отмены заказа"""
    await state.clear()
    
    text = "❌ <b>Заказ отменен</b>\n\nВыберите действие:"
    keyboard = get_main_menu_keyboard()
    
    await safe_edit_message(callback, text, keyboard)
    await callback.answer()

async def send_admin_notification(bot, order_number: str, order_data: dict, username: str):
    """Отправляет уведомление в чат модерации о новом заказе"""
    if not config.MODERATION_CHAT_ID:
        logging.warning("MODERATION_CHAT_ID не настроен, уведомление не отправлено")
        return
    
    set_type_text = get_set_type_text(order_data.get("set_type"), order_data)
    
    text = (
        f"🆕 <b>Новый заказ</b>\n\n"
        f"👤 <b>Исполнитель:</b> @{username}\n"
        f"📋 <b>Номер заказа:</b> {order_number}\n"
        f"🔹 <b>Тип:</b> {set_type_text}\n"
        f"💰 <b>Цена:</b> {order_data.get('price', 0):,} руб."
    )
    
    # Добавляем дополнительную информацию только для дисков
    if order_data.get("set_type") in ["single", "set"]:
        size = order_data.get('size', 'Не указан')
        alumochrome_text = "Да" if order_data.get("alumochrome", False) else "Нет"
        text += f"\n📏 <b>Размер:</b> {size}\n✨ <b>Алюмохром:</b> {alumochrome_text}"
    
    try:
        from keyboards import get_admin_order_keyboard
        await bot.send_photo(
            chat_id=config.MODERATION_CHAT_ID,
            photo=order_data["photo_file_id"],
            caption=text,
            parse_mode="HTML",
            reply_markup=get_admin_order_keyboard(order_number)
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
