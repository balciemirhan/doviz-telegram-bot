# keyboards.py
# <-- Telegram'daki tüm butonları oluşturur.
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from . import constants as c


def create_persistent_keyboard() -> ReplyKeyboardMarkup:
    """Sohbetin altında kalıcı olarak duran ana menü klavyesini oluşturur."""
    keyboard = [[KeyboardButton(c.BTN_DOVIZ), KeyboardButton(c.BTN_MADEN)]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def create_doviz_menu_keyboard() -> InlineKeyboardMarkup:
    """Döviz alt menüsünü oluşturur."""
    keyboard = [
        [
            InlineKeyboardButton("🇺🇸 Dolar", callback_data=c.USD),
            InlineKeyboardButton("🇪🇺 Euro", callback_data=c.EUR),
        ],
        [InlineKeyboardButton("🇬🇧 Sterlin", callback_data=c.GBP)],
    ]
    return InlineKeyboardMarkup(keyboard)


def create_metal_menu_keyboard() -> InlineKeyboardMarkup:
    """Kıymetli madenler ana menüsünü oluşturur."""
    keyboard = [
        [
            InlineKeyboardButton(
                "⚜️ Altın Çeşitleri", callback_data=c.CB_MENU_ALTIN_CESITLERI
            )
        ],
        [InlineKeyboardButton("🥈 Gram Gümüş", callback_data=c.GUMUS)],
    ]
    return InlineKeyboardMarkup(keyboard)


def create_altin_cesitleri_menu_keyboard() -> InlineKeyboardMarkup:
    """Tüm altın çeşitlerini listeleyen alt menüyü oluşturur."""
    keyboard = [
        [
            InlineKeyboardButton("Gram Altın", callback_data=c.GRAM_ALTIN),
            InlineKeyboardButton("Çeyrek Altın", callback_data=c.CEYREK_ALTIN),
        ],
        [
            InlineKeyboardButton("Yarım Altın", callback_data=c.YARIM_ALTIN),
            InlineKeyboardButton("Tam Altın", callback_data=c.TAM_ALTIN),
        ],
        [
            InlineKeyboardButton("Cumhuriyet A.", callback_data=c.CUMHURIYET_ALTINI),
            InlineKeyboardButton("Ata Altın", callback_data=c.ATA_ALTIN),
        ],
        [InlineKeyboardButton("22 Ayar Bilezik", callback_data=c.BILEZIK_22_AYAR)],
        [InlineKeyboardButton("↩️ Geri", callback_data=c.CB_MENU_METAL)],
    ]
    return InlineKeyboardMarkup(keyboard)


def create_back_menu_keyboard(back_menu: str) -> InlineKeyboardMarkup:
    """Sadece 'Geri' butonunu içeren bir klavye oluşturur."""
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("↩️ Geri", callback_data=back_menu)]]
    )
