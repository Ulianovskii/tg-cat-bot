# test_api.py
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("HUGGINGFACE_API_KEY")
print(f"Token: {token}")
print(f"Token length: {len(token) if token else 0}")