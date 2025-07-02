import requests
import datetime

TELEGRAM_BOT_TOKEN = "8120815368:AAEgT8aGpdI1SQHbMQ_6l7TJ4NDdhIlpl20"
TELEGRAM_CHAT_ID = "5031035694"

def enviar_notificacion_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensaje,
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("Notificación de Telegram enviada exitosamente.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar la notificación de Telegram: {e}")
        return False
    