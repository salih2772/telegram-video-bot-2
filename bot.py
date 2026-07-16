import random
import telebot
import os
import time
import threading
import http.server
import socketserver

API_TOKEN = '8911565294:AAHV62Zuwq9TOvKY2Nn6anRhDRXgP0hlfZc'
bot = telebot.TeleBot(API_TOKEN)

# Dosya isimleri
VIDEO_FILE = "videolar.txt"
USER_FILE = "kullanicilar.txt"

# Dosyalardan verileri yükleyen fonksiyonlar
def dosya_oku_liste(dosya_adi):
    if os.path.exists(dosya_adi):
        with open(dosya_adi, "r") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    return []

def dosya_yaz_ekle(dosya_adi, veri):
    with open(dosya_adi, "a") as f:
        f.write(f"{veri}\n")

# Canlı listeleri dosyadan dolduruyoruz
AKTIF_VIDEOLAR = dosya_oku_liste(VIDEO_FILE)
AKTIF_KULLANICILAR = set(dosya_oku_liste(USER_FILE))

@bot.message_handler(content_types=['video'])
def video_kaydet(message):
    file_id = message.video.file_id
    if file_id not in AKTIF_VIDEOLAR:
        AKTIF_VIDEOLAR.append(file_id)
        dosya_yaz_ekle(VIDEO_FILE, file_id) # Kalıcı olarak kaydet
    bot.reply_to(message, f"✅ Video hafızaya alındı! Toplam video sayısı: {len(AKTIF_VIDEOLAR)}")

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = str(message.chat.id)
    if chat_id not in AKTIF_KULLANICILAR:
        AKTIF_KULLANICILAR.add(chat_id)
        dosya_yaz_ekle(USER_FILE, chat_id) # Kalıcı olarak kaydet
    bot.reply_to(message, "🚀 Bot aktif! Kanalındaki videoları bana yönlendir, sırayla paylaşayım.")

def video_gonder():
    while True:
        time.sleep(60)  # Her 60 saniyede bir gönderim yapar
        
        # Güncel listeleri kontrol et
        if AKTIF_VIDEOLAR and AKTIF_KULLANICILAR:
            secilen_video = random.choice(AKTIF_VIDEOLAR)
            for user_id in list(AKTIF_KULLANICILAR):
                try:
                    bot.send_video(chat_id=int(user_id), video=secilen_video, caption="🎬 İşte günün videosu!")
                except Exception as e:
                    print("Gönderim hatası:", e)

# Arka plan thread'leri
threading.Thread(target=lambda: bot.polling(non_stop=True), daemon=True).start()
threading.Thread(target=video_gonder, daemon=True).start()

# Render Web Sunucusu
class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot calisiyor!")

port = int(os.environ.get("PORT", 10000))
with socketserver.TCPServer(("", port), MyHandler) as httpd:
    httpd.serve_forever()
