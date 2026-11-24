import os
import time
import threading
import asyncio
import requests
import telebot
from telebot import apihelper, types
from aiohttp import web

# --- НАСТРОЙКИ ---
TOKEN = "1780243440:wwabkG2Y_TLBq7iiyZMOKIePv-Z7RJpJLmv"
PORT = int(os.environ.get("PORT", 10000))
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL", "")
ADMIN_ID = None  # Заполнится автоматически при первом входе админа

# Перенаправляем запросы на Shuzagram API
apihelper.API_URL = "https://api.shuzagram.com/bot{0}/{1}"
bot = telebot.TeleBot(TOKEN)

# URL вашего развернутого фронтенда на GitHub Pages (измените под себя при необходимости)
WEBAPP_URL = "https://anton1212xc-hue.github.io/github.io/"

@bot.message_handler(commands=['start'])
def cmd_start(message):
    markup = types.InlineKeyboardMarkup()
    web_app = types.WebAppInfo(url=WEBAPP_URL)
    markup.add(types.InlineKeyboardButton(text="🦍 Открыть Gorilla Case", web_app=web_app))
    
    bot.send_message(
        message.chat.id,
        "👋 <b>Добро пожаловать в Gorilla Case!</b>\n\n"
        "Gorilla Case – это не обычное казино которое закроется через день, а казино на несколько месяцев с большим разнообразием и обновлениями. Удачи выйграть свое нфт!",
        reply_markup=markup,
        parse_mode="HTML"
    )

# Обработка данных из Mini App (например, запрос на вывод)
@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
    try:
        import json
        data = json.loads(message.web_app_data.data)
        user = message.from_user
        
        if data.get("action") == "withdraw":
            amount = data.get("balance", 0)
            text = (
                "📤 <b>Новая заявка на вывод звёзд!</b>\n\n"
                f"👤 Игрок: {user.first_name} (@{user.username or 'нет'})\n"
                f"🆔 ID: <code>{user.id}</code>\n"
                f"⭐ Сумма: <b>{amount} звёзд</b>\n"
                f"🎯 Куда выводить: <b>@yeban</b>"
            )
            # Если админ уже заходил, отправляем ему напрямую, иначе в чат
            target_admin = ADMIN_ID if ADMIN_ID else user.id
            bot.send_message(target_admin, text, parse_mode="HTML")
            bot.reply_to(message, "✅ Заявка на вывод успешно отправлена администратору!")
    except Exception as e:
        print(f"Ошибка обработки web_app_data: {e}")

# --- ВЕБ-СЕРВЕР И САМОПИНГ ДЛЯ RENDER ---
async def handle_ping(request):
    return web.Response(text="Gorilla Case Bot is alive!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"Веб-сервер запущен на порту {PORT}")

def run_web_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_web_server())
    loop.run_forever()

def self_ping_worker():
    time.sleep(10)
    while True:
        try:
            if RENDER_EXTERNAL_URL:
                requests.get(RENDER_EXTERNAL_URL, timeout=10)
        except Exception:
            pass
        time.sleep(30)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_web_server, daemon=True)
    server_thread.start()

    ping_thread = threading.Thread(target=self_ping_worker, daemon=True)
    ping_thread.start()
    
    print("Бот Gorilla Case успешно запущен!")
    bot.infinity_polling(skip_pending=True)
