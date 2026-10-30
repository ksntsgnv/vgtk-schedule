import os

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "НЕ НАЙДЕН")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "НЕ НАЙДЕН")

print("=" * 50)
print("ПРОВЕРКА SECRETS:")
print("=" * 50)
print(f"Токен (первые 25 символов): {TELEGRAM_BOT_TOKEN[:25]}...")
print(f"Chat ID: {TELEGRAM_CHAT_ID}")
print("=" * 50)

# Проверим, совпадает ли токен с ожидаемым
expected_token_start = "9133871343:AAGt7DDz"
if TELEGRAM_BOT_TOKEN.startswith(expected_token_start):
    print("✅ Токен совпадает с ожидаемым!")
else:
    print(f"❌ Токен НЕ совпадает! Ожидалось начало: {expected_token_start}")

if TELEGRAM_CHAT_ID == "1542128677":
    print("✅ Chat ID совпадает!")
else:
    print(f"❌ Chat ID НЕ совпадает! Ожидалось: 1542128677")
