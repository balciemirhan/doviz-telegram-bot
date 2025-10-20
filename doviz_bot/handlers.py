# handlers.py
# <-- Kullanıcıdan gelen tüm komut ve butonları karşılar.
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

# Kendi modüllerimizi "bu klasörün içinden" diye belirtiyoruz
from . import constants as c
from . import keyboards
from . import data_fetcher
from . import nlp_processor


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start komutu verildiğinde kullanıcıyı karşılar."""
    user = update.effective_user
    await update.message.reply_markdown_v2(
        f"Merhaba {user.mention_markdown_v2()}\\! 👋\n\nGüncel piyasa verileri için aşağıdaki menüyü kullanabilirsiniz\\.",
        reply_markup=keyboards.create_persistent_keyboard(),
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kullanıcıdan gelen tüm metin mesajlarını işler."""
    text = update.message.text

    # --- YENİ EKLENEN NLP KONTROLÜ ---
    # 1. Önce gelen mesajın içinde bir ürün var mı diye NLP beynimize soralım.
    item_code = nlp_processor.find_item_in_text(text)

    if item_code:
        # Eğer bir ürün bulunduysa, direkt fiyatını gösterelim.
        price_data = data_fetcher.get_market_data(data_code=item_code)
        await update.message.reply_text(
            text=price_data, parse_mode=ParseMode.MARKDOWN_V2
        )
        return  # Fonksiyonu burada bitir, aşağıya devam etmesin.
    # --- NLP KONTROLÜ SONU ---

    # 2. Eğer NLP bir şey bulamadıysa, kalıcı klavye butonlarına basılmış mı diye kontrol edelim.
    elif text == c.BTN_DOVIZ:
        await update.message.reply_text(
            "Lütfen bir döviz kuru seçin:",
            reply_markup=keyboards.create_doviz_menu_keyboard(),
        )
    elif text == c.BTN_MADEN:
        await update.message.reply_text(
            "Lütfen bir maden türü seçin:",
            reply_markup=keyboards.create_metal_menu_keyboard(),
        )

    # 3. Eğer ikisi de değilse, kullanıcı alakasız bir şey yazmıştır.
    else:
        await update.message.reply_text(
            "Anlayamadım. Lütfen aşağıdaki menüden bir işlem seçin veya bir ürün adı yazın (örn: 'dolar ne kadar?').",
            reply_markup=keyboards.create_persistent_keyboard(),
        )


async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mesaj içi (inline) buton tıklamalarını yönetir."""
    query = update.callback_query
    await query.answer()
    choice = query.data

    # Menü yönlendirmeleri
    if choice == c.CB_MENU_DOVIZ:
        await query.edit_message_text(
            text="Lütfen bir döviz kuru seçin:",
            reply_markup=keyboards.create_doviz_menu_keyboard(),
        )
    elif choice == c.CB_MENU_METAL:
        await query.edit_message_text(
            text="Lütfen bir maden türü seçin:",
            reply_markup=keyboards.create_metal_menu_keyboard(),
        )
    elif choice == c.CB_MENU_ALTIN_CESITLERI:
        await query.edit_message_text(
            text="Lütfen bir altın türü seçin:",
            reply_markup=keyboards.create_altin_cesitleri_menu_keyboard(),
        )
    # Veri getirme işlemleri
    else:
        await query.edit_message_text(text="Veriler alınıyor, lütfen bekleyin...")
        price_data = data_fetcher.get_market_data(data_code=choice)

        back_menu = None
        if choice in [c.USD, c.EUR, c.GBP]:
            back_menu = c.CB_MENU_DOVIZ
        elif choice == c.GUMUS:
            back_menu = c.CB_MENU_METAL
        else:
            back_menu = c.CB_MENU_ALTIN_CESITLERI

        await query.edit_message_text(
            text=price_data,
            reply_markup=keyboards.create_back_menu_keyboard(back_menu),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
