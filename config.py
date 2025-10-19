# config.py

import os
import logging
from dotenv import load_dotenv

# .env dosyasındaki ortam değişkenlerini yükler.
load_dotenv()

# --- AKILLI TOKEN SEÇİMİ ---
IS_PRODUCTION = os.getenv("IS_PRODUCTION", "false").lower() == "true"

if IS_PRODUCTION:
    # Bu değişken Render'ın Environment kısmında ayarlı olmalı
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
else:
    # Bu değişken .env dosyasında ayarlı olmalı
    TELEGRAM_TOKEN = os.getenv("DEV_TELEGRAM_TOKEN")

# Render'ın kullanacağı portu ortam değişkenlerinden alır.
PORT = int(os.environ.get("PORT", 8443))

# Logging'i (hata takibi) merkezi bir yerden etkinleştiriyoruz.
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

logger.info(
    f"Uygulama {'Production' if IS_PRODUCTION else 'Development'} modunda çalışıyor."
)
