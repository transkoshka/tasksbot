import os
from dotenv import load_dotenv
load_dotenv()
import asyncio
import requests
import nest_asyncio
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

# 🔐 Секреты
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# 📜 Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text.strip()

    if message_text.startswith("todo"):
        task_text = message_text.replace("todo", "").strip()
        try:
            response = requests.post(WEBHOOK_URL, json={"task": "добавь задачу: " + task_text})
            if response.status_code == 200:
                await update.message.reply_text("✅ Задача добавлена в таблицу!")
            else:
                await update.message.reply_text(f"⚠️ Ошибка при добавлении задачи. Код: {response.status_code}")
        except Exception as e:
            await update.message.reply_text(f"🚫 Ошибка отправки: {e}")
    else:
        await update.message.reply_text("👀 Я реагирую только на команды вида `#задача ...`")

# 🧠 Основной запуск
async def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✨ Бот запускается через webhook...")
    await application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        webhook_url=os.environ["RENDER_EXTERNAL_URL"] + "/webhook"
    )

# 🚀 Поехали
if __name__ == '__main__':
    nest_asyncio.apply()
    asyncio.run(main())
