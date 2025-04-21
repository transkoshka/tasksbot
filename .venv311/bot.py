from dotenv import load_dotenv
load_dotenv()

import os
import asyncio
import nest_asyncio
import requests
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

# 🔐 Вставь свои ключи
TELEGRAM_TOKEN = os.getenv("7735357077:AAGSWIyVysU5a4DK6F8Qsdl1EOpFIeeyMok")
WEBHOOK_URL = os.getenv("https://script.google.com/macros/s/AKfycbzhCvZDrcinAYHl5LYp-59a9l5PzYPRyOnI1JJXVNRO9yXBs8lJw3iT6T2KIY6flIkq/exec")

# 📜 Обработка входящих сообщений
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
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен. Ожидаю сообщения...")
    await app.run_polling()

# 🚀 Запуск
if __name__ == '__main__':
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())
