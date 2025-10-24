import os
from dotenv import load_dotenv

load_dotenv()
print("HUGGINGFACE_API_KEY:", os.getenv('HUGGINGFACE_API_KEY'))
print("Длина ключа:", len(os.getenv('HUGGINGFACE_API_KEY', '')))
