# Gerekli kütüphaneleri içe aktarıyoruz
import requests
import logging
import os
import threading
from flask import Flask
from dotenv import load_dotenv
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    helpers,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from telegram.constants import ParseMode

# .env dosyasındaki ortam değişkenlerini yüklüyoruz
load_dotenv()

# --- AKILLI TOKEN SEÇİMİ ---
# Render gibi bir "production" ortamındaysak ana token'ı,
# kendi bilgisayarımızdaysak (development) test token'ını kullanırız.
IS_PRODUCTION = os.getenv("IS_PRODUCTION", "false").lower() == "true"

if IS_PRODUCTION:
    # Bu değişken Render'ın Environment kısmında ayarlı olmalı
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
else:
    # Bu değişken .env dosyasında ayarlı olmalı
    TELEGRAM_TOKEN = os.getenv("DEV_TELEGRAM_TOKEN")

PORT = int(os.environ.get("PORT", 8443))

# Logging'i (hata takibi) etkinleştiriyoruz
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Sabitler ---
BTN_DOVIZ = "💵 Döviz Kurları"
BTN_MADEN = "⚜️ Kıymetli Madenler"
CB_MENU_DOVIZ = "menu_doviz"
CB_MENU_METAL = "menu_metal"
CB_MENU_ALTIN_CESITLERI = "menu_altin_cesitleri"
USD, EUR, GBP = "USD", "EUR", "GBP"
(
    GUMUS,
    GRAM_ALTIN,
    CEYREK_ALTIN,
    YARIM_ALTIN,
    TAM_ALTIN,
    CUMHURIYET_ALTINI,
    ATA_ALTIN,
    BILEZIK_22_AYAR,
) = (
    "gumus",
    "gram-altin",
    "ceyrek-altin",
    "yarim-altin",
    "tam-altin",
    "cumhuriyet-altini",
    "ata-altin",
    "22-ayar-bilezik",
)


# --- Klavye Oluşturma Fonksiyonları ---
def create_persistent_keyboard():
    keyboard = [[KeyboardButton(BTN_DOVIZ), KeyboardButton(BTN_MADEN)]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def create_doviz_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🇺🇸 Dolar", callback_data=USD),
            InlineKeyboardButton("🇪🇺 Euro", callback_data=EUR),
        ],
        [InlineKeyboardButton("🇬🇧 Sterlin", callback_data=GBP)],
    ]
    return InlineKeyboardMarkup(keyboard)


def create_metal_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                "⚜️ Altın Çeşitleri", callback_data=CB_MENU_ALTIN_CESITLERI
            )
        ],
        [InlineKeyboardButton("🥈 Gram Gümüş", callback_data=GUMUS)],
    ]
    return InlineKeyboardMarkup(keyboard)


def create_altin_cesitleri_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Gram Altın", callback_data=GRAM_ALTIN),
            InlineKeyboardButton("Çeyrek Altın", callback_data=CEYREK_ALTIN),
        ],
        [
            InlineKeyboardButton("Yarım Altın", callback_data=YARIM_ALTIN),
            InlineKeyboardButton("Tam Altın", callback_data=TAM_ALTIN),
        ],
        [
            InlineKeyboardButton("Cumhuriyet A.", callback_data=CUMHURIYET_ALTINI),
            InlineKeyboardButton("Ata Altın", callback_data=ATA_ALTIN),
        ],
        [InlineKeyboardButton("22 Ayar Bilezik", callback_data=BILEZIK_22_AYAR)],
        [InlineKeyboardButton("↩️ Geri", callback_data=CB_MENU_METAL)],
    ]
    return InlineKeyboardMarkup(keyboard)


def create_back_menu_keyboard(back_menu: str):
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("↩️ Geri", callback_data=back_menu)]]
    )


# --- Ana Veri Çekme Fonksiyonu ---
def get_market_data(data_code: str):
    try:
        url = "https://finans.truncgil.com/today.json"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        all_data = response.json()
        display_names = {
            USD: "💲 🇺🇸 Dolar (USD)",
            EUR: "💶 🇪🇺 Euro (EUR)",
            GBP: "💷 🇬🇧 Sterlin (GBP)",
            GUMUS: "🥈 Gram Gümüş",
            GRAM_ALTIN: "⚜️ Gram Altın",
            CEYREK_ALTIN: "⚜️ Çeyrek Altın",
            YARIM_ALTIN: "⚜️ Yarım Altın",
            TAM_ALTIN: "⚜️ Tam Altın",
            CUMHURIYET_ALTINI: "⚜️ Cumhuriyet Altını",
            ATA_ALTIN: "⚜️ Ata Altın",
            BILEZIK_22_AYAR: "⚜️ 22 Ayar Bilezik",
        }

        item_data = all_data.get(data_code)
        if not item_data:
            return helpers.escape_markdown(
                f"{data_code} için veri bulunamadı.", version=2
            )

        # Fiyatı al ve formatla
        name = display_names.get(data_code, data_code)
        name_escaped = helpers.escape_markdown(name, version=2)
        satis_fiyati_str = (
            item_data.get("Satış", "0").replace(".", "").replace(",", ".")
        )
        satis_fiyati = helpers.escape_markdown(
            f"{float(satis_fiyati_str):.2f}", version=2
        )

        # Günlük değişimi al ve formatla
        degisim_str = item_data.get("Değişim", "%0,00")
        degisim_float = float(degisim_str.replace("%", "").replace(",", "."))

        emoji = "➖"
        if degisim_float > 0:
            emoji = "📈"
            degisim_str = f"+{degisim_str}"
        elif degisim_float < 0:
            emoji = "📉"

        degisim_escaped = helpers.escape_markdown(f"({emoji} {degisim_str})", version=2)

        return f"📊 *Güncel Piyasa Fiyatı* 📊\n\n{name_escaped}: *{satis_fiyati} ₺* {degisim_escaped}"

    except Exception as e:
        logger.error(f"Veri çekme/işleme hatası: {e}")
        return helpers.escape_markdown(
            "😕 Verilere ulaşılamadı veya işlenemedi.", version=2
        )


# --- Bot Komut ve Buton İşleyicileri ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_markdown_v2(
        f"Merhaba {user.mention_markdown_v2()}\\! 👋\n\nGüncel piyasa verileri için aşağıdaki menüyü kullanabilirsiniz\\.",
        reply_markup=create_persistent_keyboard(),
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == BTN_DOVIZ:
        await update.message.reply_text(
            "Lütfen bir döviz kuru seçin:", reply_markup=create_doviz_menu_keyboard()
        )
    elif text == BTN_MADEN:
        await update.message.reply_text(
            "Lütfen bir maden türü seçin:", reply_markup=create_metal_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            "Lütfen aşağıdaki menüden bir işlem seçin.",
            reply_markup=create_persistent_keyboard(),
        )


async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    if choice == CB_MENU_DOVIZ:
        await query.edit_message_text(
            text="Lütfen bir döviz kuru seçin:",
            reply_markup=create_doviz_menu_keyboard(),
        )
    elif choice == CB_MENU_METAL:
        await query.edit_message_text(
            text="Lütfen bir maden türü seçin:",
            reply_markup=create_metal_menu_keyboard(),
        )
    elif choice == CB_MENU_ALTIN_CESITLERI:
        await query.edit_message_text(
            text="Lütfen bir altın türü seçin:",
            reply_markup=create_altin_cesitleri_menu_keyboard(),
        )
    else:
        await query.edit_message_text(text="Veriler alınıyor, lütfen bekleyin...")
        price_data = get_market_data(data_code=choice)
        back_menu = None
        if choice in [USD, EUR, GBP]:
            back_menu = CB_MENU_DOVIZ
        elif choice == GUMUS:
            back_menu = CB_MENU_METAL
        else:
            back_menu = CB_MENU_ALTIN_CESITLERI
        await query.edit_message_text(
            text=price_data,
            reply_markup=create_back_menu_keyboard(back_menu),
            parse_mode=ParseMode.MARKDOWN_V2,
        )


# --- Flask Sunucusu ve Ana Fonksiyon ---
app = Flask(__name__)


@app.route("/")
def index():
    return "Bot çalışıyor..."


def run_web_server():
    app.run(host="0.0.0.0", port=PORT)


def main() -> None:
    if not TELEGRAM_TOKEN:
        logger.error(
            "Telegram API Token bulunamadı! Lütfen .env veya Environment Variables kontrol edin."
        )
        return

    # Önce basit iş olan web sunucusunu arka planda (garson) başlatıyoruz.
    web_server_thread = threading.Thread(target=run_web_server)
    web_server_thread.daemon = True  # Ana program kapanınca bu da kapansın
    web_server_thread.start()
    logger.info("Nöbetçi Web Sunucusu arka planda başlatıldı...")

    # Sonra ana işi, yani botu, ana görevde (müdür) çalıştırıyoruz.
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(callback_query_handler))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
    )

    logger.info(
        f"Bot {'Production' if IS_PRODUCTION else 'Development'} modunda ana thread'de başlatılıyor..."
    )
    application.run_polling()


if __name__ == "__main__":
    main()
