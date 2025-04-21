import os
import asyncio
from dotenv import load_dotenv
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL") + "/webhook"
TASKS_WEBHOOK = os.getenv("WEBHOOK_URL")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.startswith("todo"):
        task = text.replace("todo", "").strip()
        try:
            res = requests.post(TASKS_WEBHOOK, json={"task": "добавь задачу: " + task})
            await update.message.reply_text("✅ Задача добавлена!" if res.status_code == 200 else f"⚠️ Ошибка: {res.status_code}")
        except Exception as e:
            await update.message.reply_text(f"🚫 {e}")
    else:
        await update.message.reply_text("👀 Команда должна начинаться с `todo`.")

async def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Не aiohttp. Просто нормальный webhook.
    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        webhook_url=WEBHOOK_URL
    )

if __name__ == '__main__':
    asyncio.run(main())
