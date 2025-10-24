# app/services/cat_analyzer.py
import aiohttp
import logging
import random
import os
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
logger = logging.getLogger(__name__)

class CatAnalyzer:
    def __init__(self, huggingface_api_key: str = HUGGINGFACE_API_KEY):
        self.huggingface_api_key = huggingface_api_key
        self.base_url = "https://api-inference.huggingface.co/models"
        logger.info(f"CatAnalyzer initialized. API key: {bool(self.huggingface_api_key)}")
        
    async def analyze_cat_image(self, image_data: bytes) -> str:
        """
        Анализирует изображение котика через Hugging Face API
        """
        try:
            logger.info("Starting real cat image analysis with HuggingFace...")
            logger.info(f"Image size: {len(image_data)} bytes")
            
            # Получаем настоящее описание от нейросети
            description = await self._get_image_description(image_data)
            logger.info(f"HuggingFace raw result: {description}")
            
            # Если API не работает, используем fallback
            if not description or description == "изображение":
                logger.warning("HuggingFace API returned empty description, using fallback")
                return self._get_fallback_response()
            
            # Проверяем что это котик
            is_cat = self._is_cat_description(description)
            if not is_cat:
                return self._get_not_cat_response(description)
            
            # Создаем смешной комментарий
            funny_comment = self._create_funny_comment(description)
            return funny_comment
            
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return self._get_fallback_response()
    
    async def _get_image_description(self, image_data: bytes) -> str:
        """Получает описание изображения от нейросети"""
        # Основная модель - самая надежная
        model = "Salesforce/blip-image-captioning-base"
        
        try:
            logger.info(f"Querying model: {model}")
            result = await self._query_huggingface(model, image_data)
            
            if result and isinstance(result, list) and len(result) > 0:
                if "error" in result:
                    logger.warning(f"Model error: {result['error']}")
                    return "изображение"
                
                description = result[0].get('generated_text', '')
                logger.info(f"Model returned: {description}")
                return description
            else:
                logger.warning("Empty result from model")
                return "изображение"
                
        except Exception as e:
            logger.error(f"Model query failed: {e}")
            return "изображение"
    
    def _is_cat_description(self, description: str) -> bool:
        """Проверяет, что описание соответствует котику"""
        description_lower = description.lower()
        
        cat_keywords = ['cat', 'kitten', 'kitty', 'feline', 'кошка', 'кот', 'котик', 'котенок']
        dog_keywords = ['dog', 'puppy', 'собака', 'пёс', 'щенок']
        
        # Если явно собака - не котик
        if any(keyword in description_lower for keyword in dog_keywords):
            return False
            
        # Если явно котик - котик
        if any(keyword in description_lower for keyword in cat_keywords):
            return True
            
        # В остальных случаях доверяем пользователю
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
        """Создает смешной комментарий"""
        # Очищаем описание от лишнего
        clean_desc = description.replace('a', '').replace('A', '').strip()
        if not clean_desc:
            clean_desc = "котик"
            
        templates = [
            f"Нейросеть видит: '{clean_desc}'. Ясно - это гениальный котик! 🧠",
            f"ИИ сообщает: '{clean_desc}'. Подозреваю, он ищет вкусняшки! 🍗",
            f"Анализ: '{clean_desc}' - профессиональный мурлыкатель! 💫",
            f"Вердикт: '{clean_desc}'. Рекомендую погладить! 🤗",
            f"Распознано: '{clean_desc}'. Эксперт по милости! 🌟",
            f"Данные: '{clean_desc}'. Уровень очарования зашкаливает! ⚡",
            f"Обнаружено: '{clean_desc}'. Мастер по растоплению сердец! 💘",
            f"Результат: '{clean_desc}'. Высший пилотаж кошачности! 🎯"
        ]
        return random.choice(templates)
    
    def _get_fallback_response(self) -> str:
        """Запасные ответы"""
        responses = [
            "Вау! Этот котик слишком милый! 🐱",
            "Уровень очарования зашкаливает! 💫",
            "Профессионал в искусстве быть милым! 🎯",
            "Особенный котик! 🌟",
            "Не могу подобрать слов для такой милоты! 🥰",
            "Этот котик явно планирует что-то грандиозное! 🌎",
            "Похоже, эксперт по пушистости за работой! 🎩",
            "Настоящий мастер кошачьих поз! 📸"
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

# Создаем экземпляр анализатора
cat_analyzer = CatAnalyzer()

# Функция для совместимости с вашим photo_handler.py
async def analyze_cat_image(image_data: bytes) -> str:
    """
    Асинхронная функция для анализа изображения
    Используется в photo_handler.py
    """
    return await cat_analyzer.analyze_cat_image(image_data)