import logging
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from handlers.fsm import EditOrderStates
from keyboards import (
    get_edit_orders_keyboard,
    get_my_orders_keyboard,
    get_order_actions_keyboard,
    get_status_keyboard,
    get_confirm_delete_keyboard,
    get_back_to_menu_keyboard,
    get_cancel_keyboard
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

async def format_order_info(order: dict) -> str:
    """Форматирует информацию о заказе с учетом профессии"""
    profession = order.get('profession', 'painter')
    
    # Определяем тип заказа
    if order['set_type'] == 'single':
        set_type_text = "один диск"
    elif order['set_type'] == 'set':
        set_type_text = "комплект"
    elif order['set_type'] == 'nakidka':
        set_type_text = "насадки"
    elif order['set_type'] == 'suspensia':
        set_type_text = "супорта"
    elif order['set_type'] == 'free':
        set_type_text = "свободный заказ"
    elif order['set_type'].startswith('70_30_'):
        disk_type = order['set_type'].split('_')[2]  # single или set
        if disk_type == 'single':
            quantity = order.get('disk_quantity', 1)
            set_type_text = f"70/30 один диск ({quantity} шт.)"
        else:
            set_type_text = "70/30 комплект"
    else:
        set_type_text = order['set_type']
    
    status_emoji = {
        'draft': '📝',
        'confirmed': '✅',
        'rejected': '❌'
    }
    
    status_text = {
        'draft': 'Черновик',
        'confirmed': 'Подтвержден',
        'rejected': 'Отклонен'
    }
    
    # Базовая информация
    text = (
        f"🆔 <b>ID:</b> {order['id']}\n"
        f"📋 <b>Номер:</b> {order['order_number']}\n"
        f"🔹 <b>Тип:</b> {set_type_text}\n"
    )
    
    # Добавляем размер только для дисков
    if order['set_type'] in ['single', 'set'] or order['set_type'].startswith('70_30_'):
        if order['size']:
            text += f"📏 <b>Размер:</b> {order['size']}\n"
    
    # Добавляем информацию в зависимости от профессии
    if profession == "painter":
        # Для маляра показываем алюмохром (только для дисков)
        if order['set_type'] in ['single', 'set'] or order['set_type'].startswith('70_30_'):
            alumochrome_text = "Да" if order['alumochrome'] else "Нет"
            text += f"✨ <b>Алюмохром:</b> {alumochrome_text}\n"
            
            # Для типа 70/30 показываем разделение дохода
            if order['set_type'].startswith('70_30_'):
                painter_70_id = order.get('painter_70_id')
                painter_30_id = order.get('painter_30_id')
                if painter_70_id and painter_30_id:
                    # Получаем имена маляров
                    painter_70_name = await db.get_user_name_by_id(painter_70_id)
                    painter_30_name = await db.get_user_name_by_id(painter_30_id)
                    total_price = order.get('price', 0)
                    price_70 = int(total_price * 0.7)
                    price_30 = int(total_price * 0.3)
                    text += f"🎨 <b>Разделение дохода:</b>\n"
                    text += f"   • {painter_70_name}: {price_70:,} руб. (70%)\n"
                    text += f"   • {painter_30_name}: {price_30:,} руб. (30%)\n"
        
        # Для супортов маляра показываем тип
        elif order['set_type'] == 'suspensia':
            suspensia_type = order.get('suspensia_type', 'paint')
            if suspensia_type == 'logo':
                text += f"🎨 <b>Тип:</b> с логотипом\n"
            else:
                text += f"🎨 <b>Тип:</b> покраска\n"
            
            quantity = order.get('quantity', 1)
            if quantity > 1:
                text += f"🔢 <b>Количество:</b> {quantity} шт.\n"
    
    else:  # sandblaster
        # Для пескоструйщика показываем напыление (только для дисков)
        if order['set_type'] in ['single', 'set']:
            spraying_deep = order.get('spraying_deep', 0)
            spraying_shallow = order.get('spraying_shallow', 0)
            
            if spraying_deep > 0 or spraying_shallow > 0:
                text += f"💨 <b>Напыление:</b>"
                if spraying_deep > 0:
                    text += f" глубоких: {spraying_deep}"
                if spraying_shallow > 0:
                    text += f" неглубоких: {spraying_shallow}"
                text += "\n"
        
        # Для супортов пескоструйщика показываем количество
        elif order['set_type'] == 'suspensia':
            quantity = order.get('quantity', 1)
            if quantity > 1:
                text += f"🔢 <b>Количество:</b> {quantity} шт.\n"
    
    # Завершаем информацию
    # Конвертируем время из UTC в часовой пояс Уфы
    tz_ufa = ZoneInfo("Asia/Yekaterinburg")
    created_at_utc = order['created_at']
    
    # Если время уже в UTC, конвертируем в Уфу
    if created_at_utc.tzinfo is None:
        # Если время naive (без timezone), считаем его UTC
        created_at_utc = created_at_utc.replace(tzinfo=ZoneInfo("UTC"))
    
    created_at_ufa = created_at_utc.astimezone(tz_ufa)
    
    text += (
        f"💰 <b>Цена:</b> {order['price']:,} руб.\n"
        f"{status_emoji.get(order['status'], '❓')} <b>Статус:</b> {status_text.get(order['status'], order['status'])}\n"
        f"📅 <b>Создан:</b> {created_at_ufa.strftime('%d.%m.%Y %H:%M')}"
    )
    
    return text

@router.callback_query(F.data == "edit_orders")
async def show_edit_orders_menu(callback: CallbackQuery, state: FSMContext):
    """Показать меню редактирования заказов"""
    await state.clear()
    
    text = "✏️ <b>Редактирование заказов</b>\n\nВыберите действие:"
    keyboard = get_edit_orders_keyboard()
    
    await safe_edit_message(callback, text, keyboard)
    await callback.answer()

@router.callback_query(F.data == "my_orders")
async def show_my_orders(callback: CallbackQuery, page: int = 0):
    """Показать заказы пользователя"""
    user_id = await db.get_or_create_user(
        callback.from_user.id,
        callback.from_user.full_name or callback.from_user.username or "Unknown"
    )
    
    # Получаем заказы с пагинацией
    orders = await db.get_user_orders_paginated(user_id, limit=5, offset=page * 5)
    total_count = await db.get_user_orders_total_count(user_id)
    
    if not orders:
        text = "📋 <b>Ваши заказы</b>\n\nУ вас пока нет заказов."
        keyboard = get_edit_orders_keyboard()
    else:
        text = f"📋 <b>Ваши заказы (стр. {page + 1}):</b>\n\n"
        for i, order in enumerate(orders, 1):
            text += f"{i}. {await format_order_info(order)}\n\n"
        text = text[:4000]  # Ограничиваем длину сообщения
        # Создаем клавиатуру с кнопками для каждого заказа и пагинацией
        keyboard = get_my_orders_keyboard(orders, page, total_count)
    
    await safe_edit_message(callback, text, keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("my_orders_page_"))
async def show_my_orders_page(callback: CallbackQuery):
    """Показать определенную страницу заказов пользователя"""
    page = int(callback.data.split("_")[3])  # my_orders_page_{page}
    
    user_id = await db.get_or_create_user(
        callback.from_user.id,
        callback.from_user.full_name or callback.from_user.username or "Unknown"
    )
    
    # Получаем заказы с пагинацией
    orders = await db.get_user_orders_paginated(user_id, limit=5, offset=page * 5)
    total_count = await db.get_user_orders_total_count(user_id)
    
    if not orders:
        text = "📋 <b>Ваши заказы</b>\n\nУ вас пока нет заказов."
        keyboard = get_edit_orders_keyboard()
    else:
        text = f"📋 <b>Ваши заказы (стр. {page + 1}):</b>\n\n"
        for i, order in enumerate(orders, 1):
            text += f"{i}. {await format_order_info(order)}\n\n"
        text = text[:4000]  # Ограничиваем длину сообщения
        # Создаем клавиатуру с кнопками для каждого заказа и пагинацией
        keyboard = get_my_orders_keyboard(orders, page, total_count)
    
    await safe_edit_message(callback, text, keyboard)
    await callback.answer()

@router.callback_query(F.data == "find_order")
async def start_find_order(callback: CallbackQuery, state: FSMContext):
    """Начать поиск заказа по номеру"""
    text = "🔍 <b>Поиск заказа</b>\n\nВведите номер заказа для поиска:"
    keyboard = get_cancel_keyboard()
    
    await safe_edit_message(callback, text, keyboard)
    await state.set_state(EditOrderStates.waiting_for_order_number)
    await callback.answer()

@router.message(StateFilter(EditOrderStates.waiting_for_order_number))
async def process_find_order_number(message: Message, state: FSMContext):
    """Обработка номера заказа для поиска"""
    if not message.text:
        await message.answer("❌ Номер заказа не может быть пустым. Попробуйте еще раз:")
        return
    
    order_number = message.text.strip()
    
    if not order_number:
        await message.answer("❌ Номер заказа не может быть пустым. Попробуйте еще раз:")
        return
    
    # Получаем user_id пользователя
    user_id = await db.get_or_create_user(
        message.from_user.id,
        message.from_user.full_name or message.from_user.username or "Unknown"
    )
    
    # Ищем заказ по номеру только среди заказов этого пользователя
    order = await db.get_user_order_by_number(user_id, order_number)
    
    if not order:
        await message.answer(
            f"❌ <b>Заказ не найден!</b>\n\n"
            f"Заказ с номером '{order_number}' не найден среди ваших заказов.\n"
            f"Проверьте правильность номера и попробуйте еще раз.",
            parse_mode="HTML",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    # Показываем информацию о заказе
    await message.answer(
        f"✅ <b>Заказ найден!</b>\n\n{format_order_info(order)}",
        parse_mode="HTML",
        reply_markup=get_order_actions_keyboard(order['id'])
    )
    
    await state.clear()

@router.callback_query(F.data.startswith("order_actions_"))
async def show_order_actions(callback: CallbackQuery):
    """Показать действия с заказом"""
    order_id = int(callback.data.split("_")[2])
    
    # Проверяем, что заказ принадлежит пользователю
    user_id = await db.get_or_create_user(
        callback.from_user.id,
        callback.from_user.full_name or callback.from_user.username or "Unknown"
    )
    
    order = await db.get_user_order_by_id(user_id, order_id)
    
    if not order:
        text = "❌ <b>Заказ не найден!</b>\n\nЗаказ не существует или не принадлежит вам."
        keyboard = get_edit_orders_keyboard()
        
        await safe_edit_message(callback, text, keyboard)
        await callback.answer("❌ Заказ не найден")
        return
    
    text = f"📋 <b>Действия с заказом</b>\n\n{await format_order_info(order)}"
    keyboard = get_order_actions_keyboard(order_id)
    
    await safe_edit_message(callback, text, keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("change_status_"))
async def start_change_status(callback: CallbackQuery):
    """Начать изменение статуса заказа"""
    order_id = int(callback.data.split("_")[2])
    
    text = "✏️ <b>Изменение статуса заказа</b>\n\nВыберите новый статус:"
    keyboard = get_status_keyboard(order_id)
    
    await safe_edit_message(callback, text, keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("set_status_"))
async def process_change_status(callback: CallbackQuery):
    """Обработка изменения статуса заказа"""
    parts = callback.data.split("_")
    order_id = int(parts[2])
    new_status = parts[3]
    
    # Проверяем, что заказ принадлежит пользователю
    user_id = await db.get_or_create_user(
        callback.from_user.id,
        callback.from_user.full_name or callback.from_user.username or "Unknown"
    )
    
    order = await db.get_user_order_by_id(user_id, order_id)
    
    if not order:
        await callback.answer("❌ Заказ не найден")
        return
    
    # Обновляем статус
    await db.update_order_status(order_id, new_status)
    
    # Получаем обновленную информацию о заказе
    updated_order = await db.get_user_order_by_id(user_id, order_id)
    
    text = f"✅ <b>Статус обновлен!</b>\n\n{format_order_info(updated_order)}"
    keyboard = get_order_actions_keyboard(order_id)
    
    await safe_edit_message(callback, text, keyboard)
    await callback.answer("✅ Статус обновлен")

@router.callback_query(F.data.startswith("change_price_"))
async def start_change_price(callback: CallbackQuery, state: FSMContext):
    """Начать изменение цены заказа"""
    order_id = int(callback.data.split("_")[2])
    
    await state.update_data(order_id=order_id)
    
    text = "💰 <b>Изменение цены заказа</b>\n\nВведите новую цену в рублях:"
    keyboard = get_cancel_keyboard()
    
    await safe_edit_message(callback, text, keyboard)
    await state.set_state(EditOrderStates.waiting_for_new_price)
    await callback.answer()

@router.message(StateFilter(EditOrderStates.waiting_for_new_price))
async def process_change_price(message: Message, state: FSMContext):
    """Обработка изменения цены заказа"""
    if not message.text:
        await message.answer("❌ Цена не может быть пустой. Попробуйте еще раз:")
        return
    
    data = await state.get_data()
    order_id = data["order_id"]
    
    try:
        new_price = int(message.text.strip())
        
        if new_price <= 0:
            await message.answer("❌ Цена должна быть больше 0. Попробуйте еще раз:")
            return
        
        # Проверяем, что заказ принадлежит пользователю
        user_id = await db.get_or_create_user(
            message.from_user.id,
            message.from_user.full_name or message.from_user.username or "Unknown"
        )
        
        order = await db.get_user_order_by_id(user_id, order_id)
        
        if not order:
            await message.answer(
                "❌ Заказ не найден!",
                reply_markup=get_edit_orders_keyboard()
            )
            await state.clear()
            return
        
        # Обновляем цену
        success = await db.update_order_price(order_id, new_price)
        
        if success:
            # Получаем обновленную информацию о заказе
            updated_order = await db.get_user_order_by_id(user_id, order_id)
            
            await message.answer(
                f"✅ <b>Цена обновлена!</b>\n\n{format_order_info(updated_order)}",
                parse_mode="HTML",
                reply_markup=get_order_actions_keyboard(order_id)
            )
        else:
            await message.answer(
                "❌ <b>Ошибка обновления цены!</b>\n\n"
                "Попробуйте еще раз или обратитесь к администратору.",
                parse_mode="HTML",
                reply_markup=get_order_actions_keyboard(order_id)
            )
    
    except ValueError:
        await message.answer("❌ Неверный формат цены. Введите число:")
        return
    
    await state.clear()

@router.callback_query(F.data.startswith("delete_order_"))
async def start_delete_order(callback: CallbackQuery):
    """Начать удаление заказа"""
    order_id = int(callback.data.split("_")[2])
    
    text = ("🗑️ <b>Удаление заказа</b>\n\n"
            "⚠️ <b>ВНИМАНИЕ!</b> Это действие нельзя отменить.\n\n"
            "Вы уверены, что хотите удалить этот заказ?")
    keyboard = get_confirm_delete_keyboard(order_id)
    
    await safe_edit_message(callback, text, keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("confirm_delete_"))
async def process_delete_order(callback: CallbackQuery):
    """Обработка удаления заказа"""
    order_id = int(callback.data.split("_")[2])
    
    # Проверяем, что заказ принадлежит пользователю
    user_id = await db.get_or_create_user(
        callback.from_user.id,
        callback.from_user.full_name or callback.from_user.username or "Unknown"
    )
    
    order = await db.get_user_order_by_id(user_id, order_id)
    
    if not order:
        await callback.answer("❌ Заказ не найден")
        return
    
    # Удаляем заказ
    success = await db.delete_order_by_id(order_id)
    
    if success:
        text = (f"✅ <b>Заказ удален!</b>\n\n"
                f"Заказ #{order_id} (номер: {order['order_number']}) успешно удален.")
        keyboard = get_edit_orders_keyboard()
        
        await safe_edit_message(callback, text, keyboard)
        await callback.answer("✅ Заказ удален")
    else:
        text = ("❌ <b>Ошибка удаления заказа!</b>\n\n"
                "Попробуйте еще раз или обратитесь к администратору.")
        keyboard = get_order_actions_keyboard(order_id)
        
        await safe_edit_message(callback, text, keyboard)
        await callback.answer("❌ Ошибка удаления")
