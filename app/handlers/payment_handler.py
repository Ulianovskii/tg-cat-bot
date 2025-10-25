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
            InlineKeyboardButton(text="3 ⭐ - 10 запросов", callback_data="buy_3"),
            InlineKeyboardButton(text="10 ⭐ - 35 запросов", callback_data="buy_10"),
        ],
        [
            InlineKeyboardButton(text="20 ⭐ - 100 запросов", callback_data="buy_20"),
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
    
    selected_package = packages[callback.data]
    
    prices = [LabeledPrice(
        label=selected_package['title'],
        amount=selected_package['stars']  # ← БЕЗ * 100 для правильного отображения
    )]
    
    await callback.bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=f"Пополнение баланса - {selected_package['title']}",
        description=f"Получите {selected_package['requests']} запросов за {selected_package['stars']} ⭐",
        payload=f"stars_{selected_package['stars']}_{callback.from_user.id}",
        provider_token="",  # Пустая строка для Stars
        currency="XTR",     # Валюта Telegram Stars
        prices=prices,
        need_name=False,
        need_phone_number=False,
        need_email=False,
        need_shipping_address=False,
        is_flexible=False,
    )
    
    await callback.answer()

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
        
        # Парсим payload: stars_3_123456789
        parts = payload.split('_')
        if len(parts) >= 3:
            stars_count = int(parts[1])
            user_id = int(parts[2])
            
            # Определяем количество запросов по количеству звезд
            requests_granted = 0
            if stars_count == 3:
                requests_granted = 10
            elif stars_count == 10:
                requests_granted = 35
            elif stars_count == 20:
                requests_granted = 100
            
            # Обновляем баланс пользователя в базе данных
            user = get_user(user_id)
            new_balance = user.paid_requests + requests_granted
            update_user_balance(user_id, new_balance)
            
            await message.answer(
                f"✅ Спасибо за покупку! Получено {requests_granted} запросов!\n"
                f"💫 Использовано {stars_count} Stars\n"
                f"📊 Теперь у вас: {new_balance} оплаченных запросов"
            )
        else:
            await message.answer("❌ Ошибка обработки платежа")
            
    except Exception as e:
        logger.error(f"❌ Error processing payment: {e}")
        await message.answer("❌ Произошла ошибка при обработке платежа")