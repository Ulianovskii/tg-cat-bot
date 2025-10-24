import os
from dotenv import load_dotenv

load_dotenv()

print("=== ENV TEST ===")
print(f"TELEGRAM_BOT_TOKEN: {os.getenv('TELEGRAM_BOT_TOKEN')}")
print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")
print(f"OPENAI length: {len(os.getenv('OPENAI_API_KEY', ''))}")
print(f"HUGGINGFACE_API_KEY: {os.getenv('HUGGINGFACE_API_KEY')}")