# app/services/openai_analyzer.py
from openai import AsyncOpenAI
import base64
import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class OpenAICatAnalyzer:
    def __init__(self):
        # Загружаем .env
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(current_dir, '..', '..')
        env_path = os.path.join(project_root, '.env')
        
        if os.path.exists(env_path):
            load_dotenv(env_path)
        else:
            load_dotenv()
        
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        # Загружаем промпт из файла
        self.prompt_text = self._load_prompt()
        
        if self.api_key:
            try:
                self.client = AsyncOpenAI(api_key=self.api_key)
                logger.info("✅ OpenAI client initialized!")
            except Exception as e:
                logger.error(f"OpenAI client error: {e}")
                self.client = None
        else:
            logger.error("OPENAI_API_KEY not found!")
            self.client = None
    
    def _load_prompt(self):
        """Загружает промпт из файла"""
        try:
            prompt_path = os.path.join(
                os.path.dirname(__file__), 
                '..', 
                'prompts', 
                'cat_prompt.txt'
            )
            
            if os.path.exists(prompt_path):
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            else:
                logger.warning("Prompt file not found, using default")
                return "Опиши этого котика на русском смешно и забавно! 2-3 предложения."
                
        except Exception as e:
            logger.error(f"Error loading prompt: {e}")
            return "Опиши этого котика на русском смешно и забавно! 2-3 предложения."
    
    async def analyze_cat_image(self, image_data: bytes) -> str:
        if not self.client:
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
                                "text": self.prompt_text
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
            logger.info(f"✅ OpenAI response: {result}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка OpenAI: {e}")
            return f"😿 Ошибка: {str(e)}"

openai_analyzer = OpenAICatAnalyzer()

async def analyze_cat_image(image_data: bytes) -> str:
    return await openai_analyzer.analyze_cat_image(image_data)