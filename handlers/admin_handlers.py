import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
# Убрали импорт Command - теперь все через кнопки

from config import config
from db import db
from keyboards import get_admin_order_keyboard

router = Router()

@router.callback_query(F.data.startswith("admin_confirm_"))
async def admin_confirm_order(callback: CallbackQuery):
    """Админ подтверждает заказ"""
    order_id = int(callback.data.split("_")[2])
    
    # Получаем данные заказа
    order = await db.get_order_by_id(order_id)
    if not order:
        await callback.answer("❌ Заказ не найден", show_alert=True)
        return
    
    # Обновляем статус заказа
    await db.update_order_status(order_id, "confirmed")
    
    # Уведомляем маляра
    try:
        await callback.bot.send_message(
            chat_id=order["tg_id"],
            text=f"✅ <b>Заказ #{order_id} подтвержден!</b>\n\n"
                 f"📋 Номер: {order['order_number']}\n"
                 f"💰 Сумма: {order['price']:,} руб.\n\n"
                 f"Спасибо за работу!",
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"Ошибка отправки уведомления маляру: {e}")
    
    # Обновляем сообщение админу
    await callback.message.edit_caption(
        caption=f"✅ <b>ЗАКАЗ ПОДТВЕРЖДЕН</b>\n\n"
                f"👤 <b>Исполнитель:</b> @{order['user_name']}\n"
                f"📋 <b>Номер заказа:</b> {order['order_number']}\n"
                f"🔹 <b>Тип:</b> {'один диск' if order['set_type'] == 'single' else 'комплект'}\n"
                f"📏 <b>Размер:</b> {order['size']}\n"
                f"✨ <b>Алюмохром:</b> {'Да' if order['alumochrome'] else 'Нет'}\n"
                f"💰 <b>Цена:</b> {order['price']:,} руб.",
        parse_mode="HTML"
    )
    
    await callback.answer("✅ Заказ подтвержден")

@router.callback_query(F.data.startswith("admin_reject_"))
async def admin_reject_order(callback: CallbackQuery):
    """Админ отклоняет заказ"""
    order_id = int(callback.data.split("_")[2])
    
    # Получаем данные заказа
    order = await db.get_order_by_id(order_id)
    if not order:
        await callback.answer("❌ Заказ не найден", show_alert=True)
        return
    
    # Обновляем статус заказа
    await db.update_order_status(order_id, "rejected")
    
    # Уведомляем маляра
    try:
        await callback.bot.send_message(
            chat_id=order["tg_id"],
            text=f"❌ <b>Заказ #{order_id} отклонен</b>\n\n"
                 f"📋 Номер: {order['order_number']}\n\n"
                 f"Обратитесь к администратору для уточнения деталей.",
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"Ошибка отправки уведомления маляру: {e}")
    
    # Обновляем сообщение админу
    await callback.message.edit_caption(
        caption=f"❌ <b>ЗАКАЗ ОТКЛОНЕН</b>\n\n"
                f"👤 <b>Исполнитель:</b> @{order['user_name']}\n"
                f"📋 <b>Номер заказа:</b> {order['order_number']}\n"
                f"🔹 <b>Тип:</b> {'один диск' if order['set_type'] == 'single' else 'комплект'}\n"
                f"📏 <b>Размер:</b> {order['size']}\n"
                f"✨ <b>Алюмохром:</b> {'Да' if order['alumochrome'] else 'Нет'}\n"
                f"💰 <b>Цена:</b> {order['price']:,} руб.",
        parse_mode="HTML"
    )
    
    await callback.answer("❌ Заказ отклонен")

@router.callback_query(F.data.startswith("admin_edit_"))
async def admin_edit_order(callback: CallbackQuery):
    """Админ хочет исправить заказ"""
    order_id = int(callback.data.split("_")[2])
    
    # Получаем данные заказа
    order = await db.get_order_by_id(order_id)
    if not order:
        await callback.answer("❌ Заказ не найден", show_alert=True)
        return
    
    # Уведомляем маляра о необходимости исправления
    try:
        await callback.bot.send_message(
            chat_id=order["tg_id"],
            text=f"✏️ <b>Заказ #{order_id} требует исправления</b>\n\n"
                 f"📋 Номер: {order['order_number']}\n\n"
                 f"Обратитесь к администратору для уточнения деталей.\n"
                 f"Для создания нового заказа отправьте фото диска(ов).",
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"Ошибка отправки уведомления маляру: {e}")
    
    await callback.answer("✏️ Маляр уведомлен о необходимости исправления")

# Убрали команду /stats - теперь все через кнопки
