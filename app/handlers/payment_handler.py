# app/handlers/payment_handler.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, LabeledPrice, SuccessfulPayment
from aiogram.filters import Command
from app.db.database import get_user, update_user_balance
import logging

payment_router = Router()
logger = logging.getLogger(__name__)


@payment_router.message(Command("replenish"))
async def replenish_balance(message: Message):
    """Показ меню пополнения через Stars"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = [
        [
            InlineKeyboardButton(text="15 ⭐ - 3 запроса", callback_data="buy_15"),
            InlineKeyboardButton(text="45 ⭐ - 10 запросов", callback_data="buy_45"),
        ],
        [
            InlineKeyboardButton(text="80 ⭐ - 20 запросов", callback_data="buy_80"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await message.answer(
        "Выберите вариант пополнения:",
        reply_markup=reply_markup
    )

@payment_router.callback_query(F.data.startswith("buy_"))
async def handle_buy_callback(callback: CallbackQuery):
    """Создание инвойса с Stars"""
    packages = {
        "buy_15": {"stars": 15, "requests": 3, "title": "15 звезд - 3 запроса"},
        "buy_45": {"stars": 45, "requests": 10, "title": "45 звезд - 10 запросов"}, 
        "buy_80": {"stars": 80, "requests": 20, "title": "80 звезд - 20 запросов"}
    }
    
    # Добавляем защиту от несуществующих пакетов
    if callback.data not in packages:
        await callback.answer(f"❌ Пакет {callback.data} не найден", show_alert=True)
        return
    
    selected_package = packages[callback.data]
    
    try:
        # Отправляем сообщение с кнопкой оплаты Stars
        await callback.bot.send_message(
            chat_id=callback.message.chat.id,
            text=(
                f"💫 **{selected_package['title']}**\n"
                f"📊 Получите {selected_package['requests']} запросов\n"
                f"💰 Стоимость: {selected_package['stars']} ⭐\n\n"
                f"Для оплаты нажмите кнопку ниже:"
            ),
            reply_markup={
                "inline_keyboard": [[{
                    "text": f"💳 Оплатить {selected_package['stars']} ⭐",
                    "pay": True
                }]]
            }
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error sending payment message: {e}")
        await callback.answer("❌ Ошибка при создании платежа", show_alert=True)

@payment_router.pre_checkout_query()
async def precheckout_handler(pre_checkout_query: PreCheckoutQuery):
    """Подтверждение платежа"""
    await pre_checkout_query.answer(ok=True)

@payment_router.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    """Обработка успешного платежа через Stars"""
    try:
        payment = message.successful_payment
        payload = payment.invoice_payload
        user_id = message.from_user.id
        
        logger.info(f"Processing payment: {payload} for user {user_id}")
        
        # Парсим payload: stars_15_123456789
        parts = payload.split('_')
        if len(parts) >= 3:
            stars_count = int(parts[1])
            
            # Определяем количество запросов по количеству звезд (оригинальные значения)
            requests_granted = 0
            if stars_count == 15:
                requests_granted = 3
            elif stars_count == 45:
                requests_granted = 10  
            elif stars_count == 80:
                requests_granted = 20
            else:
                requests_granted = stars_count // 5  # fallback
                
            # Получаем пользователя
            user = get_user(user_id)
            logger.info(f"User found: ID={user.id}, TG_ID={user.tg_id}, Paid={user.paid_requests}")
            
            # Обновляем баланс
            new_balance = user.paid_requests + requests_granted
            update_user_balance(user_id, new_balance)
            
            await message.answer(
                f"✅ Спасибо за покупку! Получено {requests_granted} запросов!\n"
                f"💫 Использовано {stars_count} Stars\n"
                f"📊 Теперь у вас: {new_balance} оплаченных запросов"
            )
            
            logger.info(f"Successfully added {requests_granted} requests to user {user_id}. New balance: {new_balance}")
                
        else:
            await message.answer("❌ Ошибка обработки платежа")
            
    except Exception as e:
        logger.error(f"❌ Error processing payment: {e}")
        await message.answer("❌ Произошла ошибка при обработке платежа")

@payment_router.message(Command("balance"))
async def check_balance(message: Message):
    """Проверить текущий баланс запросов"""
    user_id = message.from_user.id
    user = get_user(user_id)
    
    await message.answer(
        f"💰 Ваш баланс запросов:\n"
        f"• 🆓 Бесплатных: {user.free_requests}\n"
        f"• 💰 Оплаченных: {user.paid_requests}\n"
        f"• 📅 Сброс бесплатных: {user.last_reset}"
    )