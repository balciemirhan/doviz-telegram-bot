# data_fetcher.py

import requests
from telegram import helpers
import constants as c
from config import logger


def get_market_data(data_code: str):
    """API'den piyasa verisini çeker ve kullanıcıya gönderilecek hazır formatlanmış bir metin oluşturur."""
    try:
        url = "https://finans.truncgil.com/today.json"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        all_data = response.json()

        item_data = all_data.get(data_code)
        if not item_data:
            return helpers.escape_markdown(
                f"{data_code} için veri bulunamadı.", version=2
            )

        # Fiyatı al ve formatla
        name = c.DISPLAY_NAMES.get(data_code, data_code)
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
        emoji = "📈" if degisim_float > 0 else "📉" if degisim_float < 0 else "➖"
        if degisim_float > 0:
            degisim_str = f"+{degisim_str}"
        degisim_escaped = helpers.escape_markdown(f"({emoji} {degisim_str})", version=2)

        return f"📊 *Güncel Piyasa Fiyatı* 📊\n\n{name_escaped}: *{satis_fiyati} ₺* {degisim_escaped}"

    except Exception as e:
        logger.error(f"Veri çekme/işleme hatası: {e}")
        return helpers.escape_markdown(
            "😕 Verilere ulaşılamadı veya işlenemedi.", version=2
        )
