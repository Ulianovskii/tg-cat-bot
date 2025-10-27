# app/handlers/photo_handler.py
from aiogram import types
from aiogram.dispatcher.router import Router
from app.bot_instance import bot
#from app.services.cat_analyzer import analyze_cat_image
import logging

logger = logging.getLogger(__name__)
router = Router()  # ← ДОБАВЬТЕ ЭТУ СТРОЧКУ!

@router.message(lambda message: message.photo is not None)
async def handle_cat_photo(message: types.Message):
    """Обработчик фото котика"""
    try:
        user_id = message.from_user.id
        
        # Проверяем есть ли доступные запросы
        user = get_user(user_id)
        
        if user.paid_requests > 0:
            # Используем платный запрос
            use_paid_request(user_id)
            request_type = "💰 оплаченный"
        elif user.free_requests > 0:
            # Используем бесплатный запрос  
            use_free_request(user_id)
            request_type = "🆓 бесплатный"
        else:
            await message.answer(
                "😿 У вас закончились запросы!\n"
                "Используйте /replenish чтобы купить больше анализов."
            )
            return
        
        await message.answer(f"🔍 Анализирую котика... (использован {request_type} запрос)")
        
        # Скачиваем фото
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        
        # Анализируем через нейросеть
        analysis_result = await analyze_cat_image(downloaded_file.read())
        
        # Отправляем результат
        await message.answer(f"😸 {analysis_result}")
        
    except Exception as e:
        logger.error(f"Error processing cat photo: {e}")
        await message.answer("😿 Не удалось проанализировать фото. Попробуй еще раз!")