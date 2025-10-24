# Временный тест - создай test_openai.py
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key exists: {bool(api_key)}")
print(f"Key starts with: {api_key[:10] if api_key else 'None'}")