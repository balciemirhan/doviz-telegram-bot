# Döviz & Altın Takip Telegram Botu 🇹🇷

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

Bu proje, Türkiye piyasaları için anlık döviz ve kıymetli maden verilerini sunan, interaktif ve 7/24 aktif bir Telegram botudur. Kullanıcı dostu arayüzü sayesinde, güncel piyasa verilerine komut ezberlemeye gerek kalmadan, butonlar aracılığıyla kolayca ulaşılabilir.

---

## 🤖 Bota Ulaşın!

Botu canlı olarak denemek ve kullanmak için aşağıdaki linke tıklayabilirsiniz:

**[👉 Buraya Tıklayarak Bota Ulaşabilirsiniz!](https://t.me/DovizTakip_bot)**

---

## ✅ Özellikler

- **Anlık Fiyatlar:** Dolar, Euro, Sterlin gibi popüler döviz kurları ile Gram, Çeyrek, Cumhuriyet Altını gibi kıymetli madenlerin en güncel alış ve satış fiyatları.
- **Günlük Değişim Yüzdesi:** Her varlığın fiyatının yanında, o günkü artış veya azalış yüzdesini `(📈 +0.75%)` veya `(📉 -0.25%)` şeklinde gösterir.
- **Geniş Varlık Yelpazesi:** Döviz kurlarının yanı sıra, en çok takip edilen altın çeşitleri ve gümüş fiyatlarını içerir.
- **İnteraktif Menüler:**
    - **Kalıcı Klavye:** Sohbet ekranının altında her zaman duran ana menü butonları.
    - **Mesaj İçi Butonlar:** Alt menüler ve geri butonları ile kolay ve sezgisel bir gezinme deneyimi.

---

## 🛠️ Kullanılan Teknolojiler

Bu projenin hayata geçirilmesinde aşağıdaki teknolojiler ve kütüphaneler kullanılmıştır:

- **🐍 Python 3.10+:** Projenin ana programlama dili.
- **🤖 `python-telegram-bot`:** Telegram Bot API ile etkileşim kurmamızı sağlayan ana kütüphane.
- **🌐 `Flask`:** Render'ın ücretsiz "Web Service" planını kullanabilmek için oluşturulan "sahte" web sunucusu.
- **⚙️ `threading`:** Telegram botu (polling) ile Flask web sunucusunun aynı anda, birbirini engellemeden çalışmasını sağlayan kütüphane.
- **☁️ `Render`:** Botun 7/24 çalışması için bulutta barındırıldığı (hosting) platform.
- **⏰ `UptimeRobot`:** Render'ın ücretsiz servislerinin uyku moduna geçmesini engellemek için kullanılan harici "uyandırma" servisi.

---

## 🏗️ Mimari ve Yayınlama Süreci (Pipeline)

Bu bot, sürekli ve kesintisiz çalışabilmesi için özel bir "hile" mekanizması üzerine kurulmuştur. İşte bu mekanizmanın adım adım işleyişi:

### Problem: "Sürekli Çalışan Program" vs. "Ücretsiz Hosting"

Telegram botları, "polling" yöntemiyle çalıştıkları için sürekli aktif kalması gereken programlardır. Ancak Render gibi ücretsiz hosting platformları, genellikle sadece web siteleri ("Web Service") için ücretsiz plan sunar ve bu servislerin belirli bir süre işlem yapılmadığında "uyku moduna" geçmesini bekler.

### Çözüm: 3 Aşamalı Akıllı Sistem

Bu sorunu aşmak için 3 aşamalı bir sistem kurduk:

#### 1. Nöbetçi Asker: Flask 💂
- **Neden?** Render'ın "Web Service" planını kandırmak için.
- **Nasıl?** Kodun içine, dışarıdan bir istek geldiğinde sadece "Bot çalışıyor..." diyen çok basit bir Flask web sunucusu ekledik. Render, bu adresi kontrol ettiğinde bir web sitesinin çalıştığını sanır ve mutlu olur. Bu sırada asıl işi yapan Telegram botu, arka planda çalışmaya devam eder.

#### 2. Uyku Engelleyici: UptimeRobot ⏰
- **Neden?** Render'ın, 15 dakika boyunca hiç istek almayan web servislerini "uyku moduna" almasını engellemek için.
- **Nasıl?** UptimeRobot adında ücretsiz bir servis, her 5 dakikada bir bizim Flask "nöbetçimizin" adresine bir istek gönderir. Bu, Render'ın "Bu site sürekli kullanılıyor" sanmasını sağlar ve botun uykuya dalmasını **kalıcı olarak engeller.**

#### 3. Orkestra Şefi: Threading 🎻
- **Neden?** Hem Flask web sunucusunun (Nöbetçi) hem de Telegram botunun (Asıl İşçi) aynı anda, birbirini engellemeden çalışabilmesi için.
- **Nasıl?** Ana program (Müdür), en önemli iş olan Telegram botunu yönetirken; daha basit bir iş olan web sunucusunu arka planda çalışan bir "garsona" (`threading.Thread`) devreder.

### Özet Pipeline:

`💻 (Yerel Geliştirme)` -> `🐙 (GitHub'a Push)` -> `☁️ (Render Otomatik Algılar)` -> `⚙️ (Flask Hilesi ile Deploy Başarılı Olur)` -> `🤖 (Bot Canlı)`

Ve döngü: `⏰ (UptimeRobot her 5 dk'da bir)` -> `☁️ (Render'a Ping Atar)` -> `🤖 (Bot Asla Uyumaz)`

---

## 🚀 Yerel Kurulum (Kendi Bilgisayarında Çalıştırma)

Bu projeyi kendi bilgisayarınızda denemek isterseniz:

1.  **Projeyi Klonlayın:**
    ```bash
    git clone [https://github.com/balciemirhan/doviz-telegram-bot.git](https://github.com/balciemirhan/doviz-telegram-bot.git)
    cd doviz-telegram-bot
    ```

2.  **Sanal Ortam Oluşturun ve Aktif Edin:**
    ```bash
    python -m venv venv
    # Windows için:
    .\venv\Scripts\activate
    # macOS/Linux için:
    source venv/bin/activate
    ```

3.  **Gerekli Kütüphaneleri Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ortam Değişkenlerini Ayarlayın:**
    - Proje ana dizininde `.env` adında bir dosya oluşturun.
    - İçine test için kullanacağınız botun token'ını ekleyin:
      ```
      DEV_TELEGRAM_TOKEN=12345:ABCDE...
      ```

5.  **Botu Çalıştırın:**
    ```bash
    python bot.py
    ```
    Kod, `IS_PRODUCTION` ortam değişkeni olmadığı için otomatik olarak `DEV_TELEGRAM_TOKEN`'ı kullanacaktır.
