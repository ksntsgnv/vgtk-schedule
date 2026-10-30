import os
import requests

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

print(f"Токен полностью: '{TELEGRAM_BOT_TOKEN}'")
print(f"Длина токена: {len(TELEGRAM_BOT_TOKEN)}")
print(f"Токен в байтах: {TELEGRAM_BOT_TOKEN.encode('utf-8')}")
print(f"Chat ID из secrets: '{TELEGRAM_CHAT_ID}'")
print(f"Длина Chat ID: {len(str(TELEGRAM_CHAT_ID))}")
print(f"Chat ID в байтах: {TELEGRAM_CHAT_ID.encode('utf-8')}")

# Попробуем с захардкоженным правильным ID
HARDCODED_CHAT_ID = "1542128677"
print(f"\nПробуем с захардкоженным ID: {HARDCODED_CHAT_ID}")

url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
data = {
    "chat_id": HARDCODED_CHAT_ID,
    "text": "Тест с захардкоженным Chat ID!"
}

response = requests.post(url, data=data)
print(f"Ответ: {response.text}")

if response.status_code == 200:
    print("✅ Сработало с захардкоженным ID!")
else:
    print("❌ Не сработало даже с правильным ID")
