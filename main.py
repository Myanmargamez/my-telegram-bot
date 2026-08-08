import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from openai import OpenAI

# Logging Setup
logging.basicConfig(level=logging.INFO)

# Environment Variables မှ Tokens များ ရယူခြင်း
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Render မှပေးသော App URL (e.g. https://your-app.onrender.com)

# Flask Server & Telegram Bot setup
app = Flask(__name__)
bot_app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
client = OpenAI(api_key=OPENAI_API_KEY)

# AI Reply Function
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text

    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a friendly Telegram group assistant. Reply concisely in Burmese."
                },
                {"role": "user", "content": user_text}
            ],
            temperature=0.7
        )

        reply = response.choices[0].message.content
        await update.message.reply_text(reply)

    except Exception as e:
        logging.error(f"Error calling OpenAI API: {e}")

# Telegram Handler ပေါင်းထည့်ခြင်း
bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

# Webhook Route (Telegram မှ မက်ဆေ့ဂျ်များ ပို့ပေးမည့် အကွက်)
@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def webhook():
    if request.method == "POST":
        async def process():
            await bot_app.initialize()
            update = Update.de_json(request.get_json(force=True), bot_app.bot)
            await bot_app.process_update(update)
            await bot_app.shutdown()

        import asyncio
        asyncio.run(process())
        return "OK", 200

@app.route("/")
def index():
    return "Bot is running on Webhook!", 200

# Webhook Set လုပ်သည့် Function
def set_webhook():
    if TELEGRAM_BOT_TOKEN and WEBHOOK_URL:
        import requests
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}"
        r = requests.get(url)
        logging.info(f"Set Webhook Result: {r.json()}")

# Render ပေါ်စတင်ချိန်တွင် Webhook တန်းချိတ်ရန်
set_webhook()
