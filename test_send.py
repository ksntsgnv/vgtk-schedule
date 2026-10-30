import os
import requests

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

print(f"Токен: {TELEGRAM_BOT_TOKEN[:20]}...")
print(f"Chat ID: {TELEGRAM_CHAT_ID}")
print(f"Тип Chat ID: {type(TELEGRAM_CHAT_ID)}")

# Пробуем отправить простое текстовое сообщение
url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
data = {
    "chat_id": TELEGRAM_CHAT_ID,
    "text": "Тестовое сообщение от GitHub Actions!"
}

print(f"\nОтправляю запрос на: {url}")
print(f"Данные: {data}")

response = requests.post(url, data=data)
print(f"\nОтвет Telegram: {response.text}")
print(f"Status code: {response.status_code}")

if response.status_code == 200:
    print("\n✅ Сообщение отправлено!")
else:
    print(f"\n❌ Ошибка!")
