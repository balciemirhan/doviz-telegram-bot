# Gerekli kütüphaneleri içe aktarıyoruz
import requests
import logging
import os
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

# Token'ı GÜVENLİ bir şekilde ortam değişkenlerinden alıyoruz.
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Logging'i (hata takibi) etkinleştiriyoruz
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# --- Sabitler ---
# Kalıcı Klavye Buton Metinleri
BTN_DOVIZ = "💵 Döviz Kurları"
BTN_MADEN = "⚜️ Kıymetli Madenler"

# Callback Data (Mesaj İçi Buton Kimlikleri)
CB_MENU_DOVIZ = "menu_doviz"
CB_MENU_METAL = "menu_metal"
CB_MENU_ALTIN_CESITLERI = "menu_altin_cesitleri"
# CB_START_OVER SABİTİ GEREKSİZ OLDUĞU İÇİN KALDIRILDI

# Veri Butonları
USD = "USD"
EUR = "EUR"
GBP = "GBP"
GUMUS = "gumus"
GRAM_ALTIN = "gram-altin"
CEYREK_ALTIN = "ceyrek-altin"
YARIM_ALTIN = "yarim-altin"
TAM_ALTIN = "tam-altin"
CUMHURIYET_ALTINI = "cumhuriyet-altini"
ATA_ALTIN = "ata-altin"
BILEZIK_22_AYAR = "22-ayar-bilezik"


# --- Klavye Oluşturma Fonksiyonları ---


def create_persistent_keyboard() -> ReplyKeyboardMarkup:
    """Sohbetin altında kalıcı olarak duran ana menü klavyesini oluşturur."""
    keyboard = [[KeyboardButton(BTN_DOVIZ), KeyboardButton(BTN_MADEN)]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def create_doviz_menu_keyboard() -> InlineKeyboardMarkup:
    """Döviz alt menüsü (mesaj içi) klavyesini oluşturur."""
    # "Ana Menü" butonu kaldırıldı
    keyboard = [
        [
            InlineKeyboardButton("🇺🇸 Dolar", callback_data=USD),
            InlineKeyboardButton("🇪🇺 Euro", callback_data=EUR),
        ],
        [InlineKeyboardButton("🇬🇧 Sterlin", callback_data=GBP)],
    ]
    return InlineKeyboardMarkup(keyboard)


def create_metal_menu_keyboard() -> InlineKeyboardMarkup:
    """Kıymetli madenler ana menüsünü (mesaj içi) oluşturur."""
    # "Ana Menü" butonu kaldırıldı
    keyboard = [
        [
            InlineKeyboardButton(
                "⚜️ Altın Çeşitleri", callback_data=CB_MENU_ALTIN_CESITLERI
            )
        ],
        [InlineKeyboardButton("🥈 Gram Gümüş", callback_data=GUMUS)],
    ]
    return InlineKeyboardMarkup(keyboard)


def create_altin_cesitleri_menu_keyboard() -> InlineKeyboardMarkup:
    """Tüm altın çeşitlerini listeleyen alt menüyü (mesaj içi) oluşturur."""
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


def create_back_menu_keyboard(back_menu: str) -> InlineKeyboardMarkup:
    """Sadece 'Geri' butonunu içeren bir klavye oluşturur."""
    # "Ana Menü" butonu kaldırıldı
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("↩️ Geri", callback_data=back_menu)]]
    )


# --- Ana Veri Çekme Fonksiyonu --- (Değişiklik yok)
def get_market_data(data_code: str) -> str:
    try:
        url = "https://finans.truncgil.com/today.json"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
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
        name = display_names.get(data_code, data_code)
        name_escaped = helpers.escape_markdown(name, version=2)
        satis_fiyati_str = (
            item_data.get("Satış", "0").replace(".", "").replace(",", ".")
        )
        satis_fiyati = helpers.escape_markdown(
            f"{float(satis_fiyati_str):.2f}", version=2
        )
        return f"📊 *Güncel Piyasa Fiyatı* 📊\n\n{name_escaped}: *{satis_fiyati} ₺*"
    except requests.exceptions.RequestException as e:
        logger.error(f"API isteği sırasında hata: {e}")
        return helpers.escape_markdown("😕 Piyasa verilerine ulaşılamıyor.", version=2)
    except Exception as e:
        logger.error(f"Veri işlenirken hata: {e}")
        return helpers.escape_markdown("Veriler işlenirken hata oluştu.", version=2)


# --- Bot Komut ve Buton İşleyicileri ---


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start komutu verildiğinde kullanıcıyı karşılar ve kalıcı menüyü gösterir."""
    user = update.effective_user
    await update.message.reply_markdown_v2(
        f"Merhaba {user.mention_markdown_v2()}\\! 👋\n\n"
        f"Güncel piyasa verileri için aşağıdaki menüyü kullanabilirsiniz\\.",
        reply_markup=create_persistent_keyboard(),
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Kalıcı klavyeden gelen metin mesajlarını işler ve ilgili mesaj içi menüyü açar."""
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
        # Tanımlanmayan bir metin gelirse, ana menüyü hatırlat
        await update.message.reply_text(
            "Lütfen aşağıdaki menüden bir işlem seçin.",
            reply_markup=create_persistent_keyboard(),
        )


async def callback_query_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Mesaj içi (inline) buton tıklamalarını yönetir."""
    query = update.callback_query
    await query.answer()
    choice = query.data

    # "Ana Menü" butonu kaldırıldığı için o bölüm de silindi.

    # Menü yönlendirmeleri
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

    # Veri getirme işlemleri
    else:
        await query.edit_message_text(text="Veriler alınıyor, lütfen bekleyin...")
        price_data = get_market_data(data_code=choice)

        # Geri butonunun doğru menüye dönmesini sağlayan mantık
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


def main() -> None:
    if not TELEGRAM_TOKEN:
        logger.error("Telegram API Token bulunamadı! .env dosyasını kontrol edin.")
        return

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(callback_query_handler))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
    )

    logger.info("Bot başarıyla başlatıldı...")
    application.run_polling()


if __name__ == "__main__":
    main()


