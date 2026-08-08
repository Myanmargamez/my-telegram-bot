import os
import requests
from flask import Flask, request
from google import genai

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

def set_webhook():
    if TELEGRAM_BOT_TOKEN and WEBHOOK_URL:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}"
        try:
            res = requests.get(url)
            print("Set Webhook Result:", res.json())
        except Exception as e:
            print("Webhook setup error:", e)

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if data and "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"]["text"]

        reply_text = "ဝမ်းနည်းပါတယ်၊ AI ဘက်မှ အကြောင်းပြန်ရန် အဆင်မပြေသေးပါ။"
        
        if client:
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=user_text,
                )
                if response and response.text:
                    reply_text = response.text
            except Exception as e:
                print("Gemini API Error Detail:", e)

        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": reply_text
        }
        requests.post(telegram_url, json=payload)

    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "Bot status: Active", 200

set_webhook()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
