import logging
import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, PhotoSize, InlineKeyboardMarkup
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from handlers.fsm import OrderStates, UserStates
from keyboards import (
    get_main_menu_keyboard,
    get_set_type_keyboard, 
    get_size_keyboard, 
    get_alumochrome_keyboard,
    get_suspensia_type_keyboard,
    get_cancel_keyboard,
    get_back_to_menu_keyboard,
    get_start_keyboard,
    get_order_exists_keyboard,
    get_profession_keyboard,
    get_spraying_keyboard
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

def calculate_price(profession: str, set_type: str, size: str = None, alumochrome: bool = False, 
                   suspensia_type: str = None, quantity: int = 1, spraying_deep: int = 0, spraying_shallow: int = 0) -> int:
    """Рассчитывает цену заказа"""
    base_price = 0
    
    # Логируем для отладки
    profession_emoji = "🎨" if profession == "painter" else "💨"
    profession_name = "Маляр" if profession == "painter" else "Пескоструйщик"
    logging.info(f"💰 Расчет цены | {profession_emoji} {profession_name} | Тип: {set_type} | Размер: {size or 'Н/Д'} | Цена: {alumochrome and '+Алюмохром' or ''} {suspensia_type and f'({suspensia_type})' or ''} {quantity > 1 and f'×{quantity}' or ''} {spraying_deep > 0 and f'Глубоких:{spraying_deep}' or ''} {spraying_shallow > 0 and f'Неглубоких:{spraying_shallow}' or ''}")
    
    if profession == "sandblaster":
        # Логика для пескоструйщика
        if set_type == "nakidka":
            base_price = config.PRICE_SANDBLASTER_NAKIDKA
            logging.info(f"💰 Цена за насадки (пескоструйщик): {base_price}₽")
            return base_price
        
        elif set_type == "suspensia":
            base_price = config.PRICE_SANDBLASTER_SUSPENSIA
            total_price = base_price * quantity
            logging.info(f"💰 Цена за супорта (пескоструйщик): {base_price}₽ × {quantity} шт. = {total_price}₽")
            return total_price
        
        elif set_type == "single":
            # Цены для одиночных дисков пескоструйщика
            price_map = {
                "R12": config.PRICE_SANDBLASTER_SINGLE_R12,
                "R13": config.PRICE_SANDBLASTER_SINGLE_R13,
                "R14": config.PRICE_SANDBLASTER_SINGLE_R14,
                "R15": config.PRICE_SANDBLASTER_SINGLE_R15,
                "R16": config.PRICE_SANDBLASTER_SINGLE_R16,
                "R17": config.PRICE_SANDBLASTER_SINGLE_R17,
                "R18": config.PRICE_SANDBLASTER_SINGLE_R18,
                "R19": config.PRICE_SANDBLASTER_SINGLE_R19,
                "R20": config.PRICE_SANDBLASTER_SINGLE_R20,
                "R21": config.PRICE_SANDBLASTER_SINGLE_R21,
                "R22": config.PRICE_SANDBLASTER_SINGLE_R22,
                "R23": config.PRICE_SANDBLASTER_SINGLE_R23,
                "R24": config.PRICE_SANDBLASTER_SINGLE_R24,
            }
            base_price = price_map.get(size, 0)
            # Умножаем на количество дисков
            base_price = base_price * quantity
            
        elif set_type == "set":
            # Цены для комплектов пескоструйщика
            price_map = {
                "R12": config.PRICE_SANDBLASTER_SET_R12,
                "R13": config.PRICE_SANDBLASTER_SET_R13,
                "R14": config.PRICE_SANDBLASTER_SET_R14,
                "R15": config.PRICE_SANDBLASTER_SET_R15,
                "R16": config.PRICE_SANDBLASTER_SET_R16,
                "R17": config.PRICE_SANDBLASTER_SET_R17,
                "R18": config.PRICE_SANDBLASTER_SET_R18,
                "R19": config.PRICE_SANDBLASTER_SET_R19,
                "R20": config.PRICE_SANDBLASTER_SET_R20,
                "R21": config.PRICE_SANDBLASTER_SET_R21,
                "R22": config.PRICE_SANDBLASTER_SET_R22,
                "R23": config.PRICE_SANDBLASTER_SET_R23,
                "R24": config.PRICE_SANDBLASTER_SET_R24,
            }
            base_price = price_map.get(size, 0)
        
        # Добавляем стоимость напыления
        spraying_price = (spraying_deep * config.PRICE_SPRAYING_DEEP) + (spraying_shallow * config.PRICE_SPRAYING_SHALLOW)
        # Напыление умножаем на количество дисков
        spraying_price = spraying_price * quantity
        total_price = base_price + spraying_price
        
        logging.info(f"💰 Цена за {set_type} {size} ×{quantity} (пескоструйщик): {base_price}₽ + напыление: {spraying_price}₽ = {total_price}₽")
        return total_price
    
    else:
        # Логика для маляра (существующая)
        if set_type == "nakidka":
            base_price = config.PRICE_NAKIDKA
            logging.info(f"💰 Цена за насадки (маляр): {base_price}₽")
            return base_price
        
        elif set_type == "suspensia":
            if suspensia_type == "paint":
                base_price = config.PRICE_SUSPENSIA_PAINT
            elif suspensia_type == "logo":
                base_price = config.PRICE_SUSPENSIA_LOGO
            
            total_price = base_price * quantity
            logging.info(f"💰 Цена за супорта (маляр): {base_price}₽ × {quantity} шт. = {total_price}₽")
            return total_price
    
        # Обработка дисков для маляра
        elif set_type == "single":
            if size == "R12":
                base_price = config.PRICE_SINGLE_R12
            elif size == "R13":
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
            
            # Умножаем на количество дисков
            base_price = base_price * quantity
        
        elif set_type == "set":
            if size == "R12":
                base_price = config.PRICE_SET_R12
            elif size == "R13":
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
        
        # Добавляем доплату за алюмохром (только для дисков маляра)
        if alumochrome and set_type in ["single", "set"]:
            base_price += config.PRICE_ALUMOCHROME_EXTRA
    
    logging.info(f"💰 Итоговая цена: {base_price}₽")
    return base_price

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    # Игнорируем сообщения из чата модерации
    if str(message.chat.id) == str(config.MODERATION_CHAT_ID):
        return
    
    await state.clear()
    
    # Проверяем, есть ли уже профессия у пользователя
    user_profession = await db.get_user_profession(message.from_user.id)
    profession_emoji = "🎨" if user_profession == "painter" else "💨" if user_profession else "❓"
    profession_name = "Маляр" if user_profession == "painter" else "Пескоструйщик" if user_profession == "sandblaster" else "Неопределена"
    logging.info(f"👤 Пользователь {message.from_user.id} | Профессия: {profession_emoji} {profession_name}")
    
    if user_profession is not None:
        # Пользователь уже выбрал профессию, показываем главное меню
        if user_profession == "painter":
            text = "👋 <b>Добро пожаловать в бот для маляров!</b>\n\nВыберите действие:"
        else:
            text = "👋 <b>Добро пожаловать в бот для пескоструйщиков!</b>\n\nВыберите действие:"
        
        keyboard = get_main_menu_keyboard(user_profession)
        
        await message.answer(text, parse_mode="HTML", reply_markup=keyboard)
    else:
        # Пользователь еще не выбрал профессию
        text = "👨‍🎨 <b>Добро пожаловать!</b>\n\nВыберите вашу профессию:"
        keyboard = get_profession_keyboard()
        
        await message.answer(text, parse_mode="HTML", reply_markup=keyboard)
        await state.set_state(UserStates.waiting_for_profession)

@router.callback_query(F.data.startswith("profession_"), StateFilter(UserStates.waiting_for_profession))
async def process_profession_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора профессии при первом входе"""
    profession = callback.data.split("_")[1]  # painter или sandblaster
    
    # Создаем или обновляем пользователя (включая профессию)
    await db.get_or_create_user(
        callback.from_user.id,
        callback.from_user.full_name or callback.from_user.username or "Unknown",
        profession
    )
    
    # Показываем соответствующее приветствие
    if profession == "painter":
        text = "👋 <b>Добро пожаловать в бот для маляров!</b>\n\nВыберите действие:"
    else:
        text = "👋 <b>Добро пожаловать в бот для пескоструйщиков!</b>\n\nВыберите действие:"
    
    keyboard = get_main_menu_keyboard(profession)
    
    await safe_edit_message(callback, text, keyboard)
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "main_menu")
async def show_main_menu(callback: CallbackQuery, state: FSMContext):
    """Показать главное меню"""
    await state.clear()
    
    # Получаем профессию пользователя
    user_profession = await db.get_user_profession(callback.from_user.id)
    
    if user_profession == "painter":
        text = "👋 <b>Добро пожаловать в бот для маляров!</b>\n\nВыберите действие:"
    elif user_profession == "sandblaster":
        text = "👋 <b>Добро пожаловать в бот для пескоструйщиков!</b>\n\nВыберите действие:"
    else:
        # Если профессия не определена, показываем выбор профессии
        text = "👨‍🎨 <b>Выберите вашу профессию:</b>"
        keyboard = get_profession_keyboard()
        await safe_edit_message(callback, text, keyboard)
        await state.set_state(UserStates.waiting_for_profession)
        await callback.answer()
        return
    
    keyboard = get_main_menu_keyboard(user_profession)
    
    await safe_edit_message(callback, text, keyboard)
    await callback.answer()


@router.callback_query(F.data == "create_order")
async def start_create_order(callback: CallbackQuery, state: FSMContext):
    """Начать создание заказа"""
    # Получаем профессию пользователя из базы данных
    user_profession = await db.get_user_profession(callback.from_user.id)
    
    if user_profession is None:
        # Если профессия не определена, показываем выбор профессии
        text = "👨‍🎨 <b>Сначала выберите вашу профессию:</b>"
        keyboard = get_profession_keyboard()
        await safe_edit_message(callback, text, keyboard)
        await state.set_state(UserStates.waiting_for_profession)
        await callback.answer()
        return
    
    profession_text = "🎨 Маляр" if user_profession == "painter" else "💨 Пескоструйщик"
    text = f"📸 <b>Создание заказа ({profession_text})</b>\n\nОтправьте фото диска(ов), который нужно покрасить:"
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
    avg_earnings = await db.get_user_avg_earnings_per_day(user_id)
    
    text = (
        f"💰 <b>Заработок за сегодня:</b> {earnings:,} руб.\n\n"
        f"📊 <b>Средний заработок за день:</b> {avg_earnings:,.0f} руб."
    )
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
    
    # Получаем профессию пользователя из базы данных
    user_profession = await db.get_user_profession(message.from_user.id)
    
    if user_profession is None:
        await message.answer(
            "❌ <b>Ошибка!</b>\n\nСначала выберите вашу профессию. Нажмите /start",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(photo_file_id=photo.file_id, profession=user_profession)
    
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
    
    # Получаем профессию пользователя из базы данных
    user_profession = await db.get_user_profession(message.from_user.id)
    
    if user_profession is None:
        # Пользователь не выбрал профессию, перенаправляем на выбор
        text = "🎯 <b>Выберите вашу профессию:</b>"
        keyboard = get_profession_keyboard()
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        await state.set_state(UserStates.waiting_for_profession)
        return
    
    # Проверяем, не существует ли уже такой номер заказа среди пользователей той же профессии
    if await db.check_order_number_exists(order_number, user_profession):
        await message.answer(
            f"⚠️ <b>Заказ с номером '{order_number}' уже существует среди {user_profession}ов!</b>\n\n"
            f"Что вы хотите сделать?",
            parse_mode="HTML",
            reply_markup=get_order_exists_keyboard(order_number)
        )
        return
    
    await state.update_data(order_number=order_number, profession=user_profession)
    
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
        profession = data.get("profession", "painter")
        price = calculate_price(profession, "nakidka")
        await state.update_data(price=price)
        
        # Создаем заказ
        await create_order_from_data(callback, state)
        return
        
    elif set_type == "suspensia":
        data = await state.get_data()
        profession = data.get("profession", "painter")
        
        if profession == "sandblaster":
            # Для пескоструйщика сразу спрашиваем количество
            text = "🔸 <b>Супорта</b>\n\nВведите количество штук:"
            keyboard = get_cancel_keyboard()
            
            await safe_edit_message(callback, text, keyboard)
            await state.set_state(OrderStates.waiting_for_suspensia_quantity)
        else:
            # Для маляра выбираем тип (покраска или с логотипом)
            text = "🔸 <b>Супорта</b>\n\nВыберите тип:"
            keyboard = get_suspensia_type_keyboard()
            
            await safe_edit_message(callback, text, keyboard)
            await state.set_state(OrderStates.waiting_for_suspensia_type)
        
        await callback.answer()
        return
        
    elif set_type == "free":
        # Для свободного заказа запрашиваем цену
        text = "🆓 <b>Свободный заказ</b>\n\nВведите цену в рублях:"
        keyboard = get_cancel_keyboard()
        
        await safe_edit_message(callback, text, keyboard)
        await state.set_state(OrderStates.waiting_for_free_price)
        await callback.answer()
        return
        
    else:
        # Для дисков (single/set) проверяем тип
        if set_type == "single":
            # Для одиночных дисков сначала спрашиваем количество
            data = await state.get_data()
            profession = data.get("profession", "painter")
            
            text = "🔹 <b>Один диск</b>\n\nВведите количество дисков:"
            keyboard = get_cancel_keyboard()
            
            await safe_edit_message(callback, text, keyboard)
            await state.set_state(OrderStates.waiting_for_disk_quantity)
        else:
            # Для комплектов выбираем размер
            text = "📋 <b>Тип заказа:</b> комплект\n\nВыберите размер диска:"
            keyboard = get_size_keyboard()
            
            await safe_edit_message(callback, text, keyboard)
            await state.set_state(OrderStates.waiting_for_size)
        
        await callback.answer()

@router.message(StateFilter(OrderStates.waiting_for_disk_quantity))
async def process_disk_quantity(message: Message, state: FSMContext):
    """Обработка количества дисков"""
    if not message.text:
        await message.answer("❌ Введите количество дисков:")
        return
    
    try:
        quantity = int(message.text.strip())
        
        if quantity <= 0:
            await message.answer("❌ Количество должно быть больше 0. Попробуйте еще раз:")
            return
        
        await state.update_data(disk_quantity=quantity)
        
        # Переходим к выбору размера
        text = f"📋 Количество: {quantity} шт.\n\nВыберите размер диска:"
        keyboard = get_size_keyboard()
        
        await message.answer(text, reply_markup=keyboard)
        await state.set_state(OrderStates.waiting_for_size)
        
    except ValueError:
        await message.answer("❌ Неверный формат. Введите число:")
        return

@router.callback_query(F.data.startswith("size_"), StateFilter(OrderStates.waiting_for_size))
async def process_size(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора размера диска"""
    size = callback.data.split("_")[1]  # R15, R16, etc.
    
    logging.info(f"📏 Выбран размер диска: {size}")
    
    await state.update_data(size=size)
    
    data = await state.get_data()
    profession = data.get("profession", "painter")
    
    if profession == "sandblaster":
        # Для пескоструйщика спрашиваем про напыление
        text = f"📏 <b>Размер диска:</b> {size}\n\nБыло ли напыление?"
        keyboard = get_spraying_keyboard()
        
        await safe_edit_message(callback, text, keyboard)
        await state.set_state(OrderStates.waiting_for_spraying)
    else:
        # Для маляра спрашиваем про алюмохром
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

@router.callback_query(F.data.startswith("spraying_"), StateFilter(OrderStates.waiting_for_spraying))
async def process_spraying(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора напыления для пескоструйщика"""
    spraying_choice = callback.data.split("_")[1]  # yes или no
    
    if spraying_choice == "no":
        # Нет напыления - создаем заказ
        data = await state.get_data()
        profession = data.get("profession", "painter")
        set_type = data.get("set_type")
        size = data.get("size")
        
        price = calculate_price(profession, set_type, size, spraying_deep=0, spraying_shallow=0)
        await state.update_data(price=price, spraying_deep=0, spraying_shallow=0)
        
        await create_order_from_data(callback, state)
        return
    else:
        # Есть напыление - спрашиваем количество глубоких
        text = "💨 <b>Напыление</b>\n\nСколько было <b>глубоких</b> напылений?\n(Введите 0, если не было)"
        keyboard = get_cancel_keyboard()
        
        await safe_edit_message(callback, text, keyboard)
        await state.set_state(OrderStates.waiting_for_deep_spraying)
    
    await callback.answer()

@router.message(StateFilter(OrderStates.waiting_for_deep_spraying))
async def process_deep_spraying(message: Message, state: FSMContext):
    """Обработка количества глубоких напылений"""
    if not message.text:
        await message.answer("❌ Количество не может быть пустым. Попробуйте еще раз:")
        return
    
    try:
        deep_count = int(message.text.strip())
        
        if deep_count < 0:
            await message.answer("❌ Количество не может быть отрицательным. Попробуйте еще раз:")
            return
        
        await state.update_data(spraying_deep=deep_count)
        
        text = "💨 <b>Напыление</b>\n\nСколько было <b>неглубоких</b> напылений?\n(Введите 0, если не было)"
        keyboard = get_cancel_keyboard()
        
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        await state.set_state(OrderStates.waiting_for_shallow_spraying)
        
    except ValueError:
        await message.answer("❌ Неверный формат количества. Введите число:")
        return

@router.message(StateFilter(OrderStates.waiting_for_shallow_spraying))
async def process_shallow_spraying(message: Message, state: FSMContext):
    """Обработка количества неглубоких напылений"""
    if not message.text:
        await message.answer("❌ Количество не может быть пустым. Попробуйте еще раз:")
        return
    
    try:
        shallow_count = int(message.text.strip())
        
        if shallow_count < 0:
            await message.answer("❌ Количество не может быть отрицательным. Попробуйте еще раз:")
            return
        
        await state.update_data(spraying_shallow=shallow_count)
        
        # Рассчитываем цену и создаем заказ
        data = await state.get_data()
        profession = data.get("profession", "painter")
        set_type = data.get("set_type")
        size = data.get("size")
        spraying_deep = data.get("spraying_deep", 0)
        
        price = calculate_price(profession, set_type, size, spraying_deep=spraying_deep, spraying_shallow=shallow_count)
        await state.update_data(price=price)
        
        await create_order_from_message_data(message, state)
        
    except ValueError:
        await message.answer("❌ Неверный формат количества. Введите число:")
        return

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
        profession = data.get("profession", "painter")
        
        if profession == "sandblaster":
            # Для пескоструйщика супорты без типа
            price = calculate_price(profession, "suspensia", quantity=quantity)
        else:
            # Для маляра супорты с типом
            suspensia_type = data["suspensia_type"]
            price = calculate_price(profession, "suspensia", suspensia_type=suspensia_type, quantity=quantity)
        
        await state.update_data(price=price)
        
        # Создаем заказ
        await create_order_from_message_data(message, state)
        
    except ValueError:
        await message.answer("❌ Неверный формат количества. Введите число:")
        return

@router.message(StateFilter(OrderStates.waiting_for_free_price))
async def process_free_price(message: Message, state: FSMContext):
    """Обработка цены свободного заказа"""
    if not message.text:
        await message.answer("❌ Цена не может быть пустой. Попробуйте еще раз:")
        return
    
    try:
        price = int(message.text.strip())
        
        if price <= 0:
            await message.answer("❌ Цена должна быть больше 0. Попробуйте еще раз:")
            return
        
        await state.update_data(price=price)
        
        # Создаем заказ
        await create_order_from_message_data(message, state)
        
    except ValueError:
        await message.answer("❌ Неверный формат цены. Введите число:")
        return

async def create_order_from_message_data(message: Message, state: FSMContext):
    """Создает заказ из данных состояния для сообщений"""
    data = await state.get_data()
    
    # Получаем профессию пользователя
    user_profession = await db.get_user_profession(message.from_user.id)
    
    # Создаем заказ в базе данных
    user_id = await db.get_or_create_user(
        message.from_user.id,
        message.from_user.full_name or message.from_user.username or "Unknown"
    )
    
    # Проверяем, не существует ли уже такой номер заказа среди пользователей той же профессии
    if await db.check_order_number_exists(data["order_number"], user_profession):
        await message.answer(
            f"⚠️ <b>Заказ с номером '{data['order_number']}' уже существует среди {user_profession}ов!</b>\n\nЧто вы хотите сделать?",
            parse_mode="HTML",
            reply_markup=get_order_exists_keyboard(data["order_number"])
        )
        return
    
    try:
        # Определяем статус в зависимости от профессии
        profession = data.get("profession", "painter")
        status = "confirmed" if profession == "sandblaster" else "draft"
        
        order_id = await db.create_order(
            order_number=data["order_number"],
            user_id=user_id,
            set_type=data["set_type"],
            size=data.get("size"),
            alumochrome=data.get("alumochrome", False),
            price=data["price"],
            photo_file_id=data["photo_file_id"],
            suspensia_type=data.get("suspensia_type"),
            quantity=data.get("quantity", 1),
            spraying_deep=data.get("spraying_deep", 0),
            spraying_shallow=data.get("spraying_shallow", 0),
            status=status
        )
        
        # Красивое логирование создания заказа
        profession_emoji = "🎨" if data.get("profession") == "painter" else "💨"
        profession_name = "Маляр" if data.get("profession") == "painter" else "Пескоструйщик"
        logging.info(f"✅ ЗАКАЗ СОЗДАН | ID: {order_id} | №{data['order_number']} | {profession_emoji} {profession_name} | {data['set_type']} {data.get('size', '')} | {data['price']}₽")
        
        # Отправляем уведомление в чат модерации
        order_data = {
            "order_number": data["order_number"],
            "profession": data.get("profession", "painter"),
            "set_type": data["set_type"],
            "size": data.get("size"),
            "alumochrome": data.get("alumochrome", False),
            "suspensia_type": data.get("suspensia_type"),
            "quantity": data.get("quantity", 1),
            "spraying_deep": data.get("spraying_deep", 0),
            "spraying_shallow": data.get("spraying_shallow", 0),
            "price": data["price"],
            "photo_file_id": data["photo_file_id"]
        }
        await send_admin_notification(message.bot, data["order_number"], order_data, message.from_user.username or message.from_user.full_name, order_id)
        
        # Формируем текст подтверждения
        set_type_text = get_set_type_text(data["set_type"], data)
        price = data["price"]
        
        # Определяем сообщение в зависимости от профессии
        profession = data.get("profession", "painter")
        if profession == "sandblaster":
            status_message = "✅ Заказ выполнен и готов к работе!"
        else:
            status_message = "Заказ отправлен на рассмотрение администратору."
        
        text = (f"✅ <b>Заказ сформирован!</b>\n\n"
                f"📋 <b>Номер заказа:</b> {data['order_number']}\n"
                f"🔹 <b>Тип:</b> {set_type_text}\n"
                f"💰 <b>Цена:</b> {price:,} руб.\n\n"
                f"{status_message}")
        
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
    profession = data.get("profession", "painter")
    
    if set_type == "single":
        profession_text = "один диск"
    elif set_type == "set":
        profession_text = "комплект"
    elif set_type == "nakidka":
        profession_text = "насадки"
    elif set_type == "suspensia":
        if profession == "sandblaster":
            quantity = data.get("quantity", 1)
            profession_text = f"супорта ({quantity} шт.)"
        else:
            suspensia_type = data.get("suspensia_type")
            quantity = data.get("quantity", 1)
            if suspensia_type == "paint":
                profession_text = f"супорта покраска ({quantity} шт.)"
            elif suspensia_type == "logo":
                profession_text = f"супорта с логотипом ({quantity} шт.)"
            else:
                profession_text = f"супорта ({quantity} шт.)"
    elif set_type == "free":
        profession_text = "свободный заказ"
    else:
        profession_text = set_type
    
    # Добавляем информацию о напылении для пескоструйщика
    if profession == "sandblaster" and set_type in ["single", "set"]:
        spraying_deep = data.get("spraying_deep", 0)
        spraying_shallow = data.get("spraying_shallow", 0)
        if spraying_deep > 0 or spraying_shallow > 0:
            spraying_info = []
            if spraying_deep > 0:
                spraying_info.append(f"{spraying_deep} глубоких")
            if spraying_shallow > 0:
                spraying_info.append(f"{spraying_shallow} неглубоких")
            profession_text += f" (напыление: {', '.join(spraying_info)})"
    
    return profession_text

@router.callback_query(F.data.startswith("alumochrome_"), StateFilter(OrderStates.waiting_for_alumochrome))
async def process_alumochrome(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора алюмохрома"""
    alumochrome = callback.data.split("_")[1] == "yes"
    
    # Получаем все данные заказа
    data = await state.get_data()
    profession = data.get("profession", "painter")
    set_type = data["set_type"]
    size = data["size"]
    
    # Получаем количество дисков (для single типа)
    quantity = data.get("disk_quantity", 1)
    
    # Рассчитываем цену
    price = calculate_price(profession, set_type, size, alumochrome, quantity=quantity)
    
    # Сохраняем данные
    await state.update_data(alumochrome=alumochrome, price=price)
    
    # Создаем заказ
    await create_order_from_data(callback, state)

async def create_order_from_data(callback: CallbackQuery, state: FSMContext):
    """Создает заказ из данных состояния"""
    data = await state.get_data()
    
    # Получаем профессию пользователя
    user_profession = await db.get_user_profession(callback.from_user.id)
    
    # Создаем заказ в базе данных
    user_id = await db.get_or_create_user(
        callback.from_user.id,
        callback.from_user.full_name or callback.from_user.username or "Unknown"
    )
    
    # Проверяем, не существует ли уже такой номер заказа среди пользователей той же профессии
    if await db.check_order_number_exists(data["order_number"], user_profession):
        text = f"⚠️ <b>Заказ с номером '{data['order_number']}' уже существует среди {user_profession}ов!</b>\n\nЧто вы хотите сделать?"
        keyboard = get_order_exists_keyboard(data["order_number"])
        
        await safe_edit_message(callback, text, keyboard)
        await callback.answer("❌ Номер заказа уже существует")
        return
    
    try:
        # Определяем статус в зависимости от профессии
        profession = data.get("profession", "painter")
        status = "confirmed" if profession == "sandblaster" else "draft"
        
        order_id = await db.create_order(
            order_number=data["order_number"],
            user_id=user_id,
            set_type=data["set_type"],
            size=data.get("size"),
            alumochrome=data.get("alumochrome", False),
            price=data["price"],
            photo_file_id=data["photo_file_id"],
            suspensia_type=data.get("suspensia_type"),
            quantity=data.get("quantity", 1),
            spraying_deep=data.get("spraying_deep", 0),
            spraying_shallow=data.get("spraying_shallow", 0),
            status=status
        )
        
        # Красивое логирование создания заказа
        profession_emoji = "🎨" if data.get("profession") == "painter" else "💨"
        profession_name = "Маляр" if data.get("profession") == "painter" else "Пескоструйщик"
        logging.info(f"✅ ЗАКАЗ СОЗДАН | ID: {order_id} | №{data['order_number']} | {profession_emoji} {profession_name} | {data['set_type']} {data.get('size', '')} | {data['price']}₽")
        
        # Отправляем уведомление в чат модерации
        order_data = {
            "order_number": data["order_number"],
            "profession": data.get("profession", "painter"),
            "set_type": data["set_type"],
            "size": data.get("size"),
            "alumochrome": data.get("alumochrome", False),
            "suspensia_type": data.get("suspensia_type"),
            "quantity": data.get("quantity", 1),
            "spraying_deep": data.get("spraying_deep", 0),
            "spraying_shallow": data.get("spraying_shallow", 0),
            "price": data["price"],
            "photo_file_id": data["photo_file_id"]
        }
        await send_admin_notification(callback.bot, data["order_number"], order_data, callback.from_user.username or callback.from_user.full_name, order_id)
        
        # Формируем текст подтверждения
        set_type_text = get_set_type_text(data["set_type"], data)
        price = data["price"]
        
        # Определяем сообщение в зависимости от профессии
        profession = data.get("profession", "painter")
        if profession == "sandblaster":
            status_message = "✅ Заказ выполнен и готов к работе!"
        else:
            status_message = "Заказ отправлен на рассмотрение администратору."
        
        text = (f"✅ <b>Заказ сформирован!</b>\n\n"
                f"📋 <b>Номер заказа:</b> {data['order_number']}\n"
                f"🔹 <b>Тип:</b> {set_type_text}\n"
                f"💰 <b>Цена:</b> {price:,} руб.\n\n"
                f"{status_message}")
        
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
    
    # Получаем профессию пользователя
    user_profession = await db.get_user_profession(callback.from_user.id)
    if not user_profession:
        await callback.answer("❌ Профессия не определена", show_alert=True)
        return
    
    # Удаляем существующий заказ только для этой профессии
    deleted = await db.delete_order_by_number_and_profession(order_number, user_profession)
    
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
    
    # Получаем профессию пользователя
    user_profession = await db.get_user_profession(callback.from_user.id)
    
    text = "❌ <b>Заказ отменен</b>\n\nВыберите действие:"
    keyboard = get_main_menu_keyboard(user_profession)
    
    await safe_edit_message(callback, text, keyboard)
    await callback.answer()

async def send_admin_notification(bot, order_number: str, order_data: dict, username: str, order_id: int = None):
    """Отправляет уведомление в чат модерации о новом заказе"""
    if not config.MODERATION_CHAT_ID:
        logging.warning("MODERATION_CHAT_ID не настроен, уведомление не отправлено")
        return
    
    profession = order_data.get("profession", "painter")
    profession_text = "🎨 Маляр" if profession == "painter" else "💨 Пескоструйщик"
    
    # Получаем текст типа без информации о напылении (чтобы избежать дублирования)
    set_type = order_data.get("set_type")
    if set_type == "single":
        set_type_text = "один диск"
    elif set_type == "set":
        set_type_text = "комплект"
    elif set_type == "nakidka":
        set_type_text = "насадки"
    elif set_type == "suspensia":
        if profession == "sandblaster":
            quantity = order_data.get("quantity", 1)
            set_type_text = f"супорта ({quantity} шт.)"
        else:
            suspensia_type = order_data.get("suspensia_type")
            quantity = order_data.get("quantity", 1)
            if suspensia_type == "paint":
                set_type_text = f"супорта покраска ({quantity} шт.)"
            elif suspensia_type == "logo":
                set_type_text = f"супорта с логотипом ({quantity} шт.)"
            else:
                set_type_text = f"супорта ({quantity} шт.)"
    elif set_type == "free":
        set_type_text = "свободный заказ"
    else:
        set_type_text = set_type
    
    # Определяем отображение исполнителя
    if profession == "painter":
        executor_display = f"@{username}"
    else:
        executor_display = f"@{username}"
    
    text = (
        f"🆕 <b>Новый заказ</b>\n\n"
        f"<b>{profession_text}:</b> {executor_display}\n"
        f"📋 <b>Номер заказа:</b> {order_number}\n"
        f"🔹 <b>Тип:</b> {set_type_text}\n"
        f"💰 <b>Цена:</b> {order_data.get('price', 0):,} руб."
    )
    
    # Добавляем дополнительную информацию только для дисков
    if order_data.get("set_type") in ["single", "set"]:
        size = order_data.get('size', 'Не указан')
        text += f"\n📏 <b>Размер:</b> {size}"
        
        if profession == "painter":
            # Для маляра показываем алюмохром
            alumochrome_text = "Да" if order_data.get("alumochrome", False) else "Нет"
            text += f"\n✨ <b>Алюмохром:</b> {alumochrome_text}"
        else:
            # Для пескоструйщика показываем напыление
            spraying_deep = order_data.get("spraying_deep", 0)
            spraying_shallow = order_data.get("spraying_shallow", 0)
            if spraying_deep > 0 or spraying_shallow > 0:
                spraying_info = []
                if spraying_deep > 0:
                    spraying_info.append(f"{spraying_deep} глубоких")
                if spraying_shallow > 0:
                    spraying_info.append(f"{spraying_shallow} неглубоких")
                text += f"\n💨 <b>Напыление:</b> {', '.join(spraying_info)}"
    
    try:
        # Для пескоструйщика не показываем кнопки (заказ уже подтвержден)
        if profession == "sandblaster":
            await bot.send_photo(
                chat_id=config.MODERATION_CHAT_ID,
                photo=order_data["photo_file_id"],
                caption=text,
                parse_mode="HTML"
            )
        else:
            # Для маляра показываем кнопки подтверждения
            from keyboards import get_admin_order_keyboard
            await bot.send_photo(
                chat_id=config.MODERATION_CHAT_ID,
                photo=order_data["photo_file_id"],
                caption=text,
                parse_mode="HTML",
                reply_markup=get_admin_order_keyboard(order_number, order_id)
            )
    except Exception as e:
        logging.error(f"Ошибка отправки уведомления в чат модерации: {e}")


@router.message()
async def handle_any_message(message: Message, state: FSMContext):
    """Обработчик для всех остальных сообщений"""
    # Игнорируем сообщения из чата модерации
    if str(message.chat.id) == str(config.MODERATION_CHAT_ID):
        return
    
    # Игнорируем состояния редактирования заказов (они обрабатываются в edit_handlers.py)
    from handlers.fsm import EditOrderStates
    current_state = await state.get_state()
    
    # Проверяем, не находимся ли мы в состоянии редактирования заказов
    if (current_state == EditOrderStates.waiting_for_order_number or 
        current_state == EditOrderStates.waiting_for_new_price):
        # Эти состояния обрабатываются в edit_handlers.py, пропускаем
        return
    
    # Если пользователь не в процессе создания заказа, показываем главное меню
    if current_state is None:
        # Регистрируем пользователя в базе данных
        user_id = await db.get_or_create_user(
            message.from_user.id, 
            message.from_user.full_name or message.from_user.username or "Unknown"
        )
        
        # Получаем профессию пользователя
        user_profession = await db.get_user_profession(message.from_user.id)
        
        if user_profession == "painter":
            text = "🎨 <b>Добро пожаловать в бот для маляров!</b>\n\nВыберите действие:"
        else:
            text = "💨 <b>Добро пожаловать в бот для пескоструйщиков!</b>\n\nВыберите действие:"
        
        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard(user_profession)
        )
    else:
        # Если пользователь в процессе создания заказа, но отправил что-то не то
        await message.answer(
            "❌ Неверный формат сообщения. Используйте кнопки для навигации.",
            reply_markup=get_cancel_keyboard()
        )

@router.callback_query(F.data.startswith("price_list"))
async def show_price_list(callback: CallbackQuery):
    """Показать прайс-лист"""
    from config import config
    from keyboards import get_back_to_menu_keyboard
    
    # Определяем профессию по callback_data
    if callback.data == "price_list_painter":
        profession = "painter"
    elif callback.data == "price_list_sandblaster":
        profession = "sandblaster"
    else:
        # Если callback_data просто "price_list", получаем профессию пользователя
        profession = await db.get_user_profession(callback.from_user.id) or "painter"
    
    # Формируем прайс-лист
    if profession == "painter":
        # Прайс-лист для маляра
        text = "💰 <b>Прайс-лист маляра</b>\n\n"
        text += "🔹 <b>Один диск:</b>\n"
        text += f"R12: {config.PRICE_SINGLE_R12 + config.PRICE_PREP_SINGLE}₽\n"
        text += f"R13: {config.PRICE_SINGLE_R13 + config.PRICE_PREP_SINGLE}₽\n"
        text += f"R14: {config.PRICE_SINGLE_R14 + config.PRICE_PREP_SINGLE}₽\n"
        text += f"R15: {config.PRICE_SINGLE_R15 + config.PRICE_PREP_SINGLE}₽\n"
        text += f"R16: {config.PRICE_SINGLE_R16 + config.PRICE_PREP_SINGLE}₽\n"
        text += f"R17: {config.PRICE_SINGLE_R17 + config.PRICE_PREP_SINGLE}₽\n"
        text += f"R18: {config.PRICE_SINGLE_R18 + config.PRICE_PREP_SINGLE}₽\n"
        text += f"R19: {config.PRICE_SINGLE_R19 + config.PRICE_PREP_SINGLE}₽\n"
        text += f"R20: {config.PRICE_SINGLE_R20 + config.PRICE_PREP_SINGLE}₽\n"
        text += f"R21: {config.PRICE_SINGLE_R21 + config.PRICE_PREP_SINGLE}₽\n"
        text += f"R22: {config.PRICE_SINGLE_R22 + config.PRICE_PREP_SINGLE}₽\n"
        text += f"R23: {config.PRICE_SINGLE_R23 + config.PRICE_PREP_SINGLE}₽\n"
        text += f"R24: {config.PRICE_SINGLE_R24 + config.PRICE_PREP_SINGLE}₽\n\n"
        text += "🔹 <b>Комплект:</b>\n"
        text += f"R12: {config.PRICE_SET_R12 + config.PRICE_PREP_SET}₽\n"
        text += f"R13: {config.PRICE_SET_R13 + config.PRICE_PREP_SET}₽\n"
        text += f"R14: {config.PRICE_SET_R14 + config.PRICE_PREP_SET}₽\n"
        text += f"R15: {config.PRICE_SET_R15 + config.PRICE_PREP_SET}₽\n"
        text += f"R16: {config.PRICE_SET_R16 + config.PRICE_PREP_SET}₽\n"
        text += f"R17: {config.PRICE_SET_R17 + config.PRICE_PREP_SET}₽\n"
        text += f"R18: {config.PRICE_SET_R18 + config.PRICE_PREP_SET}₽\n"
        text += f"R19: {config.PRICE_SET_R19 + config.PRICE_PREP_SET}₽\n"
        text += f"R20: {config.PRICE_SET_R20 + config.PRICE_PREP_SET}₽\n"
        text += f"R21: {config.PRICE_SET_R21 + config.PRICE_PREP_SET}₽\n"
        text += f"R22: {config.PRICE_SET_R22 + config.PRICE_PREP_SET}₽\n"
        text += f"R23: {config.PRICE_SET_R23 + config.PRICE_PREP_SET}₽\n"
        text += f"R24: {config.PRICE_SET_R24 + config.PRICE_PREP_SET}₽\n\n"
        text += "🔸 <b>Специальные услуги:</b>\n"
        text += f"Насадки: {config.PRICE_NAKIDKA}₽\n"
        text += f"Супорта покраска: {config.PRICE_SUSPENSIA_PAINT}₽\n"
        text += f"Супорта с логотипом: {config.PRICE_SUSPENSIA_LOGO}₽\n\n"
        text += "✨ Алюмохром: +{0}₽".format(config.PRICE_ALUMOCHROME_EXTRA)
    else:
        # Прайс-лист для пескоструйщика
        text = "💰 <b>Прайс-лист пескоструйщика</b>\n\n"
        text += "🔹 <b>Один диск:</b>\n"
        text += f"R12: {config.PRICE_SANDBLASTER_SINGLE_R12}₽\n"
        text += f"R13: {config.PRICE_SANDBLASTER_SINGLE_R13}₽\n"
        text += f"R14: {config.PRICE_SANDBLASTER_SINGLE_R14}₽\n"
        text += f"R15: {config.PRICE_SANDBLASTER_SINGLE_R15}₽\n"
        text += f"R16: {config.PRICE_SANDBLASTER_SINGLE_R16}₽\n"
        text += f"R17: {config.PRICE_SANDBLASTER_SINGLE_R17}₽\n"
        text += f"R18: {config.PRICE_SANDBLASTER_SINGLE_R18}₽\n"
        text += f"R19: {config.PRICE_SANDBLASTER_SINGLE_R19}₽\n"
        text += f"R20: {config.PRICE_SANDBLASTER_SINGLE_R20}₽\n"
        text += f"R21: {config.PRICE_SANDBLASTER_SINGLE_R21}₽\n"
        text += f"R22: {config.PRICE_SANDBLASTER_SINGLE_R22}₽\n"
        text += f"R23: {config.PRICE_SANDBLASTER_SINGLE_R23}₽\n"
        text += f"R24: {config.PRICE_SANDBLASTER_SINGLE_R24}₽\n\n"
        text += "🔹 <b>Комплект:</b>\n"
        text += f"R12: {config.PRICE_SANDBLASTER_SET_R12}₽\n"
        text += f"R13: {config.PRICE_SANDBLASTER_SET_R13}₽\n"
        text += f"R14: {config.PRICE_SANDBLASTER_SET_R14}₽\n"
        text += f"R15: {config.PRICE_SANDBLASTER_SET_R15}₽\n"
        text += f"R16: {config.PRICE_SANDBLASTER_SET_R16}₽\n"
        text += f"R17: {config.PRICE_SANDBLASTER_SET_R17}₽\n"
        text += f"R18: {config.PRICE_SANDBLASTER_SET_R18}₽\n"
        text += f"R19: {config.PRICE_SANDBLASTER_SET_R19}₽\n"
        text += f"R20: {config.PRICE_SANDBLASTER_SET_R20}₽\n"
        text += f"R21: {config.PRICE_SANDBLASTER_SET_R21}₽\n"
        text += f"R22: {config.PRICE_SANDBLASTER_SET_R22}₽\n"
        text += f"R23: {config.PRICE_SANDBLASTER_SET_R23}₽\n"
        text += f"R24: {config.PRICE_SANDBLASTER_SET_R24}₽\n\n"
        text += "🔸 <b>Специальные услуги:</b>\n"
        text += f"Насадки: {config.PRICE_SANDBLASTER_NAKIDKA}₽\n"
        text += f"Супорта: {config.PRICE_SANDBLASTER_SUSPENSIA}₽\n\n"
        text += "💨 <b>Напыление:</b>\n"
        text += f"Глубокое: +{config.PRICE_SPRAYING_DEEP}₽\n"
        text += f"Неглубокое: +{config.PRICE_SPRAYING_SHALLOW}₽"
    
    keyboard = get_back_to_menu_keyboard()
    await safe_edit_message(callback, text, keyboard)
    await callback.answer()
