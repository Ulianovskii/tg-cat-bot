# test_huggingface.py
import aiohttp
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_api():
    token = os.getenv("HUGGINGFACE_API_KEY")
    print(f"Testing API with token: {bool(token)}")
    
    if not token:
        print("❌ No token found")
        return
        
    # Простой тестовый запрос
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://huggingface.co/api/whoami-v2"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    user_info = await response.json()
                    print(f"✅ API works! User: {user_info.get('name', 'Unknown')}")
                else:
                    print(f"❌ API error: {response.status}")
                    print(await response.text())
    except Exception as e:
        print(f"❌ Request failed: {e}")

asyncio.run(test_api())