import os
from dotenv import load_dotenv
import sys

load_dotenv()

secret = os.getenv('APP_SECRET')

if secret is None:
    print("Ошибка: Переменная окружения APP_SECRET не найдена!")
    sys.exit(1)

print(f"System started. Secret hash: {secret[:3]}***")