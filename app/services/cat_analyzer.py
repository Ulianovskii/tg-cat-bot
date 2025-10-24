# app/services/cat_analyzer.py
import aiohttp
import logging
import random
import os
from dotenv import load_dotenv

load_dotenv()

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
logger = logging.getLogger(__name__)

class CatAnalyzer:
    def __init__(self, huggingface_api_key: str = HUGGINGFACE_API_KEY):
        self.huggingface_api_key = huggingface_api_key
        self.base_url = "https://api-inference.huggingface.co/models"
        logger.info(f"CatAnalyzer initialized. API key: {bool(self.huggingface_api_key)}")
        
        # Словарь перевода с английского на русский
        self.translation_dict = {
            # Породы кошек
            'cat': 'котик', 'kitten': 'котенок', 'kitty': 'котик', 'feline': 'кошачий',
            'tabby': 'полосатый кот', 'siamese': 'сиамский кот', 'persian': 'персидский кот',
            'maine coon': 'мейн-кун', 'bengal': 'бенгальский кот', 'ragdoll': 'рэгдолл',
            'british shorthair': 'британская короткошерстная',
            
            # Породы собак (для фильтрации)
            'dog': 'собака', 'puppy': 'щенок', 'terrier': 'терьер',
            'american staffordshire terrier': 'американский стаффордширский терьер',
            'staffordshire terrier': 'стаффордширский терьер', 
            'american pit bull terrier': 'американский питбультерьер',
            'pit bull terrier': 'питбультерьер',
            'labrador': 'лабрадор', 'german shepherd': 'немецкая овчарка',
            'golden retriever': 'золотистый ретривер', 'poodle': 'пудель',
            
            # Общие термины
            'animal': 'животное', 'pet': 'питомец', 'domestic': 'домашний',
            'white': 'белый', 'black': 'черный', 'brown': 'коричневый',
            'orange': 'рыжий', 'gray': 'серый', 'sleeping': 'спящий',
            'sitting': 'сидящий', 'lying': 'лежащий', 'playing': 'играющий',
            'eating': 'кушающий', 'looking': 'смотрящий'
        }
        
    async def analyze_cat_image(self, image_data: bytes) -> str:
        """
        Анализирует изображение котика через Hugging Face API
        """
        try:
            logger.info("Starting real cat image analysis with HuggingFace...")
            logger.info(f"Image size: {len(image_data)} bytes")
            
            # Пробуем разные модели
            description = await self._get_image_description(image_data)
            logger.info(f"HuggingFace raw result: {description}")
            
            # Если API не работает, используем fallback
            if not description or description == "изображение":
                logger.warning("HuggingFace API returned empty description, using fallback")
                return self._get_fallback_response()
            
            # Переводим описание на русский
            russian_description = self._translate_to_russian(description)
            
            # Проверяем что это котик
            is_cat = self._is_cat_description(russian_description)
            if not is_cat:
                return self._get_not_cat_response(russian_description)
            
            # Создаем смешной комментарий на русском
            funny_comment = self._create_funny_comment(russian_description)
            return funny_comment
            
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return self._get_fallback_response()
    
    async def _get_image_description(self, image_data: bytes) -> str:
        """Получает описание изображения от нейросети"""
        # Сначала пробуем модели классификации, потом генерации
        models_to_try = [
            "microsoft/resnet-50",  # Надежная классификация
            "google/vit-base-patch16-224",  # Другая классификация
        ]
        
        for model in models_to_try:
            try:
                logger.info(f"Querying model: {model}")
                result = await self._query_huggingface(model, image_data)
                
                if result and isinstance(result, list) and len(result) > 0:
                    if "error" in result:
                        logger.warning(f"Model error: {result['error']}")
                        continue
                    
                    # Берем топ-3 предсказания для лучшего описания
                    top_predictions = result[:3]
                    description = ", ".join([pred.get('label', '') for pred in top_predictions if pred.get('label')])
                    
                    if description:
                        logger.info(f"Model returned: {description}")
                        return description
                        
            except Exception as e:
                logger.error(f"Model {model} failed: {e}")
                continue
        
        return "изображение"
    
    def _translate_to_russian(self, description: str) -> str:
        """Переводит описание с английского на русский"""
        if not description:
            return "изображение"
            
        description_lower = description.lower()
        russian_parts = []
        
        # Разбиваем описание на слова и переводим
        for word in description_lower.replace(',', ' ').split():
            clean_word = word.strip()
            if clean_word in self.translation_dict:
                russian_parts.append(self.translation_dict[clean_word])
            else:
                russian_parts.append(clean_word)
        
        russian_description = ' '.join(russian_parts)
        
        # Улучшаем читаемость
        improvements = {
            'котик котик': 'котик',
            'кот котик': 'котик', 
            'собака собака': 'собака'
        }
        
        for eng, rus in improvements.items():
            russian_description = russian_description.replace(eng, rus)
        
        logger.info(f"Translated: '{description}' -> '{russian_description}'")
        return russian_description
    
    def _is_cat_description(self, description: str) -> bool:
        """Проверяет, что описание соответствует котику"""
        description_lower = description.lower()
        
        cat_keywords = ['котик', 'кот', 'котенок', 'кошка', 'кошачий', 'котэ', 'киса']
        dog_keywords = ['собака', 'щенок', 'терьер', 'питбуль', 'стаффордширский', 'овчарка', 'ретривер']
        
        # Если явно собака - не котик
        if any(keyword in description_lower for keyword in dog_keywords):
            return False
            
        # Если явно котик - котик
        if any(keyword in description_lower for keyword in cat_keywords):
            return True
            
        # В остальных случаях доверяем пользователю (он же отправил фото "котика")
        return True
    
    def _get_not_cat_response(self, description: str) -> str:
        """Ответ когда загружено не фото котика"""
        responses = [
            f"Хм... '{description}'. Это не котик! 🚫 Пришли фото котика!",
            f"'{description}' - интересно, но я жду котика! 😾",
            f"Похоже, это '{description}'. Я специализируюсь на котиках! 🐱"
        ]
        return random.choice(responses)
    
    def _create_funny_comment(self, description: str) -> str:
        """Создает смешной комментарий на русском"""
        # Очищаем описание
        clean_desc = description
        if not clean_desc or clean_desc == 'изображение':
            clean_desc = "котик"
            
        templates = [
            f"Нейросеть видит: '{clean_desc}'. Ясно - это гениальный котик! 🧠",
            f"ИИ сообщает: '{clean_desc}'. Подозреваю, он ищет вкусняшки! 🍗",
            f"Анализ: '{clean_desc}' - профессиональный мурлыкатель! 💫",
            f"Вердикт: '{clean_desc}'. Рекомендую погладить! 🤗",
            f"Распознано: '{clean_desc}'. Эксперт по милости! 🌟",
            f"Данные: '{clean_desc}'. Уровень очарования зашкаливает! ⚡",
            f"Обнаружено: '{clean_desc}'. Мастер по растоплению сердец! 💘",
        ]
        return random.choice(templates)
    
    def _get_fallback_response(self) -> str:
        """Запасные ответы когда нейросеть не работает"""
        responses = [
            "Вау! Этот котик слишком милый! 🐱",
            "Уровень очарования зашкаливает! 💫", 
            "Профессионал в искусстве быть милым! 🎯",
            "Особенный котик! 🌟",
            "Не могу подобрать слов для такой милоты! 🥰",
        ]
        return random.choice(responses)
    
    async def _query_huggingface(self, model: str, image_data: bytes):
        """Запрос к Hugging Face API"""
        if not self.huggingface_api_key:
            logger.warning("No HuggingFace API key provided")
            return None
            
        headers = {
            "Authorization": f"Bearer {self.huggingface_api_key}",
        }
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(
                    f"{self.base_url}/{model}",
                    headers=headers,
                    data=image_data
                ) as response:
                    
                    logger.info(f"API response status: {response.status}")
                    
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"API success: {result}")
                        return result
                    elif response.status == 503:
                        error_text = await response.text()
                        logger.warning(f"Model loading: {error_text}")
                        return {"error": "model_loading"}
                    else:
                        error_text = await response.text()
                        logger.error(f"API error {response.status}: {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return None

cat_analyzer = CatAnalyzer()

async def analyze_cat_image(image_data: bytes) -> str:
    return await cat_analyzer.analyze_cat_image(image_data)