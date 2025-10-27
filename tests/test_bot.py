#!/usr/bin/env python3
import os
from dotenv import load_dotenv

print("=== ТЕСТ ЗАГРУЗКИ .env ===")

# Пробуем загрузить .env разными способами
load_dotenv()

print("Текущая директория:", os.getcwd())
print(".env путь:", os.path.abspath('.env'))

# Проверим все переменные
print("BOT_TOKEN:", bool(os.getenv('BOT_TOKEN')))
print("ADMIN_ID:", os.getenv('ADMIN_ID'))
print("DATABASE_URL:", bool(os.getenv('DATABASE_URL')))
print("HUGGINGFACE_API_KEY:", bool(os.getenv('HUGGINGFACE_API_KEY')))

# Если ключ не найден, проверим вручную
if not os.getenv('HUGGINGFACE_API_KEY'):
    print("\n🔍 Проверяем .env вручную:")
    try:
        with open('.env', 'r') as f:
            content = f.read()
            print("Содержимое .env:")
            print(content)
    except Exception as e:
        print(f"Ошибка чтения .env: {e}")
