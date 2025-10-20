# nlp_processor.py
# Bu dosya, kullanıcıdan gelen metni analiz edip içinden ürün kodunu bulur.

from . import constants as c

# Kullanıcıların yazabileceği farklı ifadeleri, sistem kodlarımıza çeviren sözlük.
KEYWORD_MAP = {
    # Döviz
    "dolar": c.USD,
    "doları": c.USD,
    "amerikan doları": c.USD,
    "usd": c.USD,
    "euro": c.EUR,
    "avro": c.EUR,
    "eur": c.EUR,
    "sterlin": c.GBP,
    "pound": c.GBP,
    "gbp": c.GBP,
    # Gümüş
    "gümüş": c.GUMUS,
    "gumus": c.GUMUS,
    # Altın
    "gram altın": c.GRAM_ALTIN,
    "gram": c.GRAM_ALTIN,
    "çeyrek altın": c.CEYREK_ALTIN,
    "çeyrek": c.CEYREK_ALTIN,
    "ceyrek": c.CEYREK_ALTIN,
    "yarım altın": c.YARIM_ALTIN,
    "yarım": c.YARIM_ALTIN,
    "yarim": c.YARIM_ALTIN,
    "tam altın": c.TAM_ALTIN,
    "tam": c.TAM_ALTIN,
    "cumhuriyet altını": c.CUMHURIYET_ALTINI,
    "cumhuriyet": c.CUMHURIYET_ALTINI,
    "ata altın": c.ATA_ALTIN,
    "ata": c.ATA_ALTIN,
    "22 ayar bilezik": c.BILEZIK_22_AYAR,
    "bilezik": c.BILEZIK_22_AYAR,
}


def find_item_in_text(text: str) -> str | None:
    """
    Verilen metnin içinde bilinen bir ürün anahtar kelimesi arar.
    Bulursa, sistem kodunu (örn: 'gram-altin') döndürür. Bulamazsa, None döndürür.
    """
    # Gelen metni küçük harfe çevirerek daha kolay arama yapıyoruz.
    lower_text = text.lower()

    # En uzun anahtar kelimeden en kısaya doğru arama yapmak daha doğru sonuç verir.
    # Örneğin, "gram altın" kelimesini "gram"dan önce bulması gerekir.
    for keyword in sorted(KEYWORD_MAP.keys(), key=len, reverse=True):
        if keyword in lower_text:
            return KEYWORD_MAP[keyword]

    return None
