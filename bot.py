# bot.py

import threading
from flask import Flask
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

# Kendi oluşturduğumuz modülleri içe aktarıyoruz
import config
import handlers

# --- Flask Sunucusu (Render Hilesi) ---
app = Flask(__name__)


@app.route("/")
def index():
    return "Bot çalışıyor..."


def run_web_server():
    app.run(host="0.0.0.0", port=config.PORT)


# --- Ana Orkestra Şefi ---
def main() -> None:
    """Botu kurar, işleyicileri ekler ve çalıştırır."""
    if not config.TELEGRAM_TOKEN:
        config.logger.error("Telegram API Token bulunamadı!")
        return

    # Web sunucusunu arka planda başlat
    web_server_thread = threading.Thread(target=run_web_server)
    web_server_thread.daemon = True
    web_server_thread.start()
    config.logger.info("Nöbetçi Web Sunucusu arka planda başlatıldı...")

    # Telegram bot uygulamasını oluştur
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()

    # Handlers (işleyici) modülümüzden fonksiyonları ekle
    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CallbackQueryHandler(handlers.callback_query_handler))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.message_handler)
    )

    config.logger.info("Bot ana thread'de başlatılıyor...")
    application.run_polling()


if __name__ == "__main__":
    main()
