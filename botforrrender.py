import os
import asyncio
import logging
import nest_asyncio
from aiohttp import web
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

# Загружаем переменные окружения
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL") + "/webhook"
GOOGLE_WEBHOOK = os.getenv("WEBHOOK_URL")  # Сюда отправляем задачи

# Логгирование
logging.basicConfig(level=logging.INFO)

# Telegram-приложение
app = Application.builder().token(TELEGRAM_TOKEN).build()

# Обработчик сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text.strip()
    if message_text.startswith("todo"):
        task_text = message_text.replace("todo", "").strip()
        try:
            import requests
            response = requests.post(GOOGLE_WEBHOOK, json={"task": "добавь задачу: " + task_text})
            if response.status_code == 200:
                await update.message.reply_text("✅ Задача добавлена в таблицу!")
            else:
                await update.message.reply_text(f"⚠️ Ошибка. Код: {response.status_code}")
        except Exception as e:
            await update.message.reply_text(f"🚫 Ошибка отправки: {e}")
    else:
        await update.message.reply_text("👀 Используй `todo` в начале задачи.")

# Регистрируем хендлер
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# AIOHTTP сервер
async def telegram_webhook(request):
    data = await request.json()
    update = Update.de_json(data, app.bot)
    await app.process_update(update)
    return web.Response()

async def healthcheck(request):
    return web.Response(text="🔋 Bot is alive!")

async def main():
    # Настраиваем aiohttp приложение
    aio_app = web.Application()
    aio_app.router.add_post("/webhook", telegram_webhook)
    aio_app.router.add_get("/", healthcheck)

    # Запускаем webhook Telegram
    await app.bot.set_webhook(WEBHOOK_URL)
    logging.info(f"🔗 Webhook установлен: {WEBHOOK_URL}")

    runner = web.AppRunner(aio_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 8443)))
    await site.start()
    logging.info("🚀 AIOHTTP сервер запущен и слушает порт.")

if __name__ == '__main__':
    nest_asyncio.apply()
    asyncio.run(main())
