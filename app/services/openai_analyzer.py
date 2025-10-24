# app/services/openai_analyzer.py
from openai import AsyncOpenAI
import base64
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class OpenAICatAnalyzer:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)
        else:
            logger.error("OPENAI_API_KEY not found in .env")
    
    async def analyze_cat_image(self, image_data: bytes) -> str:
        """Анализ фото через GPT-4o Mini"""
        if not self.api_key:
            return "❌ OpenAI API не настроен"
        
        try:
            logger.info("🔍 Анализируем котика через GPT-4o Mini...")
            
            # Кодируем изображение
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": """
                                Опиши этого котика на русском смешно и забавно! 
                                2-3 предложения про что он делает, его эмоции и обстановку.
                                Будь оригинальным, используй русский юмор и мемы!
                                Не будь банальным - придумай что-то веселое!
                                """
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=150,
                temperature=0.9
            )
            
            result = response.choices[0].message.content
            logger.info(f"✅ GPT-4o Mini ответил: {result}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка OpenAI: {e}")
            return f"😿 Ошибка: {str(e)}"

# Создаем глобальный экземпляр
openai_analyzer = OpenAICatAnalyzer()

async def analyze_cat_image(image_data: bytes) -> str:
    return await openai_analyzer.analyze_cat_image(image_data)