# app/handlers/photo_handler.py
from aiogram import types
from aiogram.dispatcher.router import Router
from app.bot_instance import bot
from app.services.cat_analyzer import analyze_cat_image
import logging

logger = logging.getLogger(__name__)
router = Router()  # ← ДОБАВЬТЕ ЭТУ СТРОЧКУ!

@router.message(lambda message: message.photo is not None)
async def handle_cat_photo(message: types.Message):
    """Обработчик фото котика"""
    try:
        await message.answer("🔍 Анализирую котика...")
        
        # Скачиваем фото
        photo = message.photo[-1]  # Берем самое качественное фото
        file_info = await bot.get_file(photo.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        
        # Анализируем через нейросеть
        analysis_result = await analyze_cat_image(downloaded_file.read())
        
        # Отправляем результат от нейросети
        await message.answer(f"😸 {analysis_result}")
        
    except Exception as e:
        logger.error(f"Error processing cat photo: {e}")
        await message.answer("😿 Не удалось проанализировать фото. Попробуй еще раз!")