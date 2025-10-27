from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def test_balance():
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Скажи привет!"}],
            max_tokens=10
        )
        print("✅ Баланс есть! OpenAI работает!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

import asyncio
asyncio.run(test_balance())