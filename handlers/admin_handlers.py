import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
# Убрали импорт Command - теперь все через кнопки

from config import config
from db import db
from keyboards import get_admin_order_keyboard

router = Router()

def get_order_type_text(order: dict) -> str:
    """Возвращает текстовое описание типа заказа"""
    set_type = order.get('set_type')
    
    if set_type == 'single':
        return "один диск"
    elif set_type == 'set':
        return "комплект"
    elif set_type == 'nakidka':
        return "насадки"
    elif set_type == 'suspensia':
        quantity = order.get('quantity', 1)
        return f"супорта ({quantity} шт.)"
    elif set_type == 'free':
        return "свободный заказ"
    else:
        return set_type

async def is_moderator(user_id: int, chat_id: int, bot) -> bool:
    """Проверяет, является ли пользователь модератором в чате"""
    try:
        # Проверяем, является ли пользователь главным администратором бота
        if user_id == config.ADMIN_CHAT_ID:
            return True
            
        # Проверяем, есть ли пользователь в списке модераторов
        if user_id in config.MODERATORS:
            return True
            
        # Проверяем права в чате модерации (для обратной совместимости)
        if config.MODERATION_CHAT_ID:
            chat_member = await bot.get_chat_member(chat_id, user_id)
            return chat_member.status in ['administrator', 'creator']
        
        return False
    except Exception as e:
        logging.error(f"Ошибка проверки прав модератора: {e}")
        return False

@router.callback_query(F.data.startswith("admin_confirm_"))
async def admin_confirm_order(callback: CallbackQuery):
    """Модератор подтверждает заказ"""
    # Проверяем права модератора
    if not await is_moderator(callback.from_user.id, callback.message.chat.id, callback.bot):
        await callback.answer("❌ У вас нет прав для модерации заказов", show_alert=True)
        return
    
    # Проверяем формат callback_data
    parts = callback.data.split("_")
    if len(parts) >= 4 and parts[2] == "id":
        # Новый формат с ID заказа
        order_id = int(parts[3])
        order = await db.get_order_by_id(order_id)
    else:
        # Старый формат с номером заказа (обратная совместимость)
        order_number = callback.data.split("_", 2)[2]
        order = await db.get_order_by_number(order_number)
    
    if not order:
        await callback.answer("❌ Заказ не найден", show_alert=True)
        return
    
    # Обновляем статус заказа
    await db.update_order_status(order['id'], "confirmed")
    
    # Удаляем сообщение с напоминанием, если оно было отправлено
    reminder_msg_id = await db.get_reminder_message_id(order['id'])
    if reminder_msg_id:
        try:
            await callback.bot.delete_message(chat_id=config.MODERATION_CHAT_ID, message_id=reminder_msg_id)
            logging.info(f"🗑️ Удалено напоминание о заказе #{order['order_number']}")
        except Exception as e:
            logging.warning(f"Не удалось удалить сообщение с напоминанием: {e}")
    
    # Получаем username пользователя через API Telegram
    try:
        user_info = await callback.bot.get_chat(order["tg_id"])
        username = user_info.username if user_info.username else order['user_name']
    except Exception as e:
        logging.warning(f"Не удалось получить username для tg_id {order['tg_id']}: {e}")
        username = order['user_name']
    
    # Уведомляем пользователя (маляра или пескоструйщика)
    try:
        profession_text = "🎨 Маляр" if order.get('profession') == 'painter' else "💨 Пескоструйщик"
        await callback.bot.send_message(
            chat_id=order["tg_id"],
            text=f"✅ <b>Заказ подтвержден!</b>\n\n"
                 f"📋 Номер: {order['order_number']}\n"
                 f"💰 Сумма: {order['price']:,} руб.\n\n"
                 f"Спасибо за работу!",
            parse_mode="HTML"
        )
        logging.info(f"✅ УВЕДОМЛЕНИЕ ОТПРАВЛЕНО | {profession_text} | ID: {order['tg_id']} | №{order['order_number']} | {order['price']}₽")
    except Exception as e:
        logging.error(f"Ошибка отправки уведомления пользователю: {e}")
    
    # Обновляем сообщение админу
    # Определяем отображение исполнителя в зависимости от профессии
    if order.get('profession') == 'painter':
        executor_display = f"🎨 Маляр: @{username}"
    else:
        executor_display = f"💨 Пескоструйщик: @{username}"
    
    caption_text = (
        f"✅ <b>ЗАКАЗ ПОДТВЕРЖДЕН</b>\n\n"
        f"👤 <b>Исполнитель:</b> {executor_display}\n"
        f"📋 <b>Номер заказа:</b> {order['order_number']}\n"
        f"🔹 <b>Тип:</b> {get_order_type_text(order)}\n"
    )
    
    # Добавляем размер и алюмохром только для дисков
    if order['set_type'] in ['single', 'set']:
        caption_text += f"📏 <b>Размер:</b> {order['size']}\n"
        caption_text += f"✨ <b>Алюмохром:</b> {'Да' if order['alumochrome'] else 'Нет'}\n"
    
    caption_text += f"💰 <b>Цена:</b> {order['price']:,} руб."
    
    await callback.message.edit_caption(
        caption=caption_text,
        parse_mode="HTML"
    )
    
    await callback.answer("✅ Заказ подтвержден")

@router.callback_query(F.data.startswith("admin_reject_"))
async def admin_reject_order(callback: CallbackQuery):
    """Модератор отклоняет заказ"""
    # Проверяем права модератора
    if not await is_moderator(callback.from_user.id, callback.message.chat.id, callback.bot):
        await callback.answer("❌ У вас нет прав для модерации заказов", show_alert=True)
        return
    
    # Проверяем формат callback_data
    parts = callback.data.split("_")
    if len(parts) >= 4 and parts[2] == "id":
        # Новый формат с ID заказа
        order_id = int(parts[3])
        order = await db.get_order_by_id(order_id)
    else:
        # Старый формат с номером заказа (обратная совместимость)
        order_number = callback.data.split("_", 2)[2]
        order = await db.get_order_by_number(order_number)
    
    if not order:
        await callback.answer("❌ Заказ не найден", show_alert=True)
        return
    
    # Обновляем статус заказа
    await db.update_order_status(order['id'], "rejected")
    
    # Удаляем сообщение с напоминанием, если оно было отправлено
    reminder_msg_id = await db.get_reminder_message_id(order['id'])
    if reminder_msg_id:
        try:
            await callback.bot.delete_message(chat_id=config.MODERATION_CHAT_ID, message_id=reminder_msg_id)
            logging.info(f"🗑️ Удалено напоминание о заказе #{order['order_number']}")
        except Exception as e:
            logging.warning(f"Не удалось удалить сообщение с напоминанием: {e}")
    
    # Получаем username пользователя через API Telegram
    try:
        user_info = await callback.bot.get_chat(order["tg_id"])
        username = user_info.username if user_info.username else order['user_name']
    except Exception as e:
        logging.warning(f"Не удалось получить username для tg_id {order['tg_id']}: {e}")
        username = order['user_name']
    
    # Уведомляем пользователя (маляра или пескоструйщика)
    try:
        profession_text = "🎨 Маляр" if order.get('profession') == 'painter' else "💨 Пескоструйщик"
        await callback.bot.send_message(
            chat_id=order["tg_id"],
            text=f"❌ <b>Заказ отклонен</b>\n\n"
                 f"📋 Номер: {order['order_number']}\n\n"
                 f"Обратитесь к администратору для уточнения деталей.",
            parse_mode="HTML"
        )
        logging.info(f"❌ УВЕДОМЛЕНИЕ ОБ ОТКЛОНЕНИИ | {profession_text} | ID: {order['tg_id']} | №{order['order_number']}")
    except Exception as e:
        logging.error(f"Ошибка отправки уведомления об отклонении: {e}")
    
    # Обновляем сообщение админу
    # Определяем отображение исполнителя в зависимости от профессии
    if order.get('profession') == 'painter':
        executor_display = f"🎨 Маляр: @{username}"
    else:
        executor_display = f"💨 Пескоструйщик: @{username}"
    
    caption_text = (
        f"❌ <b>ЗАКАЗ ОТКЛОНЕН</b>\n\n"
        f"👤 <b>Исполнитель:</b> {executor_display}\n"
        f"📋 <b>Номер заказа:</b> {order['order_number']}\n"
        f"🔹 <b>Тип:</b> {get_order_type_text(order)}\n"
    )
    
    # Добавляем размер и алюмохром только для дисков
    if order['set_type'] in ['single', 'set']:
        caption_text += f"📏 <b>Размер:</b> {order['size']}\n"
        caption_text += f"✨ <b>Алюмохром:</b> {'Да' if order['alumochrome'] else 'Нет'}\n"
    
    caption_text += f"💰 <b>Цена:</b> {order['price']:,} руб."
    
    await callback.message.edit_caption(
        caption=caption_text,
        parse_mode="HTML"
    )
    
    await callback.answer("❌ Заказ отклонен")

@router.callback_query(F.data.startswith("admin_edit_"))
async def admin_edit_order(callback: CallbackQuery):
    """Модератор хочет исправить заказ"""
    # Проверяем права модератора
    if not await is_moderator(callback.from_user.id, callback.message.chat.id, callback.bot):
        await callback.answer("❌ У вас нет прав для модерации заказов", show_alert=True)
        return
    
    # Проверяем формат callback_data
    parts = callback.data.split("_")
    if len(parts) >= 4 and parts[2] == "id":
        # Новый формат с ID заказа
        order_id = int(parts[3])
        order = await db.get_order_by_id(order_id)
    else:
        # Старый формат с номером заказа (обратная совместимость)
        order_number = callback.data.split("_", 2)[2]
        order = await db.get_order_by_number(order_number)
    
    if not order:
        await callback.answer("❌ Заказ не найден", show_alert=True)
        return
    
    # Уведомляем пользователя о необходимости исправления
    try:
        profession_text = "🎨 Маляр" if order.get('profession') == 'painter' else "💨 Пескоструйщик"
        await callback.bot.send_message(
            chat_id=order["tg_id"],
            text=f"✏️ <b>Заказ требует исправления</b>\n\n"
                 f"📋 Номер: {order['order_number']}\n\n"
                 f"Обратитесь к администратору для уточнения деталей.\n"
                 f"Для создания нового заказа отправьте фото диска(ов).",
            parse_mode="HTML"
        )
        logging.info(f"✏️ УВЕДОМЛЕНИЕ О РЕДАКТИРОВАНИИ | {profession_text} | ID: {order['tg_id']} | №{order['order_number']}")
    except Exception as e:
        logging.error(f"Ошибка отправки уведомления о редактировании: {e}")
    
    await callback.answer("✏️ Маляр уведомлен о необходимости исправления")

# Убрали команду /stats - теперь все через кнопки
