import requests
import os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram_message(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        payload = {
            "chat_id": CHAT_ID,
            "text": text
        }

        response = requests.post(url, json=payload)

        if response.status_code == 200:
            print("Telegram message sent ✅")
        else:
            print(f"Telegram error: {response.text}")

    except Exception as e:
        print(f"Telegram exception: {e}")