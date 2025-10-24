# app/services/openai_analyzer.py
from openai import AsyncOpenAI
import base64
import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class OpenAICatAnalyzer:
    def __init__(self):
        print("=== OPENAI ANALYZER DEBUG ===")
        
        # ✅ Загружаем .env с явным путем
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(current_dir, '..', '..')
        env_path = os.path.join(project_root, '.env')
        
        print(f"📁 Current dir: {current_dir}")
        print(f"📁 Project root: {project_root}") 
        print(f"📁 ENV path: {env_path}")
        print(f"📁 ENV exists: {os.path.exists(env_path)}")
        
        if os.path.exists(env_path):
            load_dotenv(env_path)
            print("✅ .env loaded successfully")
        else:
            load_dotenv()  # Попробуем без пути
            print("⚠️  .env not found at explicit path, trying default")
        
        # ✅ Проверим ВСЕ переменные из .env
        print("🔍 Checking ALL .env variables:")
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    print(f"   {line}")
        
        # ✅ Проверим конкретно OPENAI_API_KEY
        self.api_key = os.getenv("OPENAI_API_KEY")
        print(f"🔑 OPENAI_API_KEY from env: '{self.api_key}'")
        print(f"🔑 Key length: {len(self.api_key) if self.api_key else 0}")
        
        # ✅ Загружаем промпт из файла
        self.prompt_text = self._load_prompt()
        print(f"📝 Prompt loaded: {len(self.prompt_text)} chars")
        
        # ✅ Создаем клиент
        if self.api_key:
            try:
                self.client = AsyncOpenAI(api_key=self.api_key)
                print("✅ OpenAI client initialized!")
            except Exception as e:
                print(f"❌ OpenAI client error: {e}")
                self.client = None
        else:
            print("❌ OPENAI_API_KEY is None or empty!")
            self.client = None
        
        print("=== END DEBUG ===")
    
    def _load_prompt(self):
        """Загружает промпт из файла"""
        try:
            prompt_path = os.path.join(
                os.path.dirname(__file__), 
                '..', 
                'prompts', 
                'cat_prompt.txt'
            )
            print(f"📁 Loading prompt from: {prompt_path}")
            
            if os.path.exists(prompt_path):
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    print(f"✅ Prompt loaded successfully: {len(content)} chars")
                    return content
            else:
                print("❌ Prompt file not found, using default")
                return "Опиши этого котика на русском смешно и забавно! 2-3 предложения."
                
        except Exception as e:
            print(f"❌ Error loading prompt: {e}")
            return "Опиши этого котика на русском смешно и забавно! 2-3 предложения."
    
    async def analyze_cat_image(self, image_data: bytes) -> str:
        if not self.client:
            return "❌ OpenAI API не настроен"
        
        try:
            logger.info("🔍 Анализируем котика через GPT-4o Mini...")
            print("🔄 Sending request to OpenAI...")
            print(f"📝 Using prompt: {self.prompt_text[:100]}...")  # Покажем начало промпта
            
            # Кодируем изображение
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            print(f"🔄 Image encoded, size: {len(image_base64)} chars")
            
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": self.prompt_text  # ← ИСПОЛЬЗУЕМ ПРОМПТ ИЗ ФАЙЛА
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
            print(f"✅ OpenAI response: {result}")
            return result
            
        except Exception as e:
            error_msg = f"❌ Ошибка OpenAI: {str(e)}"
            logger.error(error_msg)
            print(error_msg)
            return f"😿 Ошибка: {str(e)}"

# Создаем глобальный экземпляр
openai_analyzer = OpenAICatAnalyzer()

async def analyze_cat_image(image_data: bytes) -> str:
    return await openai_analyzer.analyze_cat_image(image_data)