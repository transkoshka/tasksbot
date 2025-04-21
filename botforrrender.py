import os
import asyncio
import requests
import nest_asyncio
from aiohttp import web
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

# 🎭 Притворяемся живыми
load_dotenv()
nest_asyncio.apply()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")
PORT = int(os.environ.get("PORT", 8443))

if not TELEGRAM_TOKEN or not RENDER_EXTERNAL_URL:
    raise RuntimeError("❌ Переменные окружения не установлены!")


# 📜 Обработка входящих сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text.strip()
    print(f"[📩] Получено сообщение: {message_text}")

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
        await update.message.reply_text("👀 Я реагирую только на команды вида `todo ...`")


# 🌐 Фальшивый сервер, чтобы Render поверил
async def start_fake_server():
    async def handle_get(request):
        return web.Response(text="Webhook bot is alive!")

    async def handle_post(request):
        data = await request.text()
        print(f"[📡] POST на /webhook: {data}")
        return web.Response(text="OK")

    app = web.Application()
    app.router.add_get("/", handle_get)
    app.router.add_post("/webhook", handle_post)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"[🌍] Фальшивый веб-сервер запущен на порту {PORT}")


# 🧠 Запуск бота
async def start_bot():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"
    await app.bot.set_webhook(webhook_url)
    print(f"[🔗] Webhook установлен: {webhook_url}")

    await app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=webhook_url
    )


# 🚀 Главная функция
async def main():
    print("[⚙️] Запуск...")
    await asyncio.gather(
        start_fake_server(),
        start_bot()
    )


if __name__ == "__main__":
    asyncio.run(main())
