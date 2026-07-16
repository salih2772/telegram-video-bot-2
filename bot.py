import random
import telebot
import os
import time
import threading
import http.server
import socketserver

API_TOKEN = '8911565294:AAHV62Zuwq9TOvKY2Nn6anRhDRXgP0hlfZc'
bot = telebot.TeleBot(API_TOKEN)
VIDEOLAR_DOSYASI = "videolar.txt"
KULLANICILAR_DOSYASI = "kullanicilar.txt"

def dosya_kaydet(dosya, veri):
    with open(dosya, "a") as f:
        f.write(f"{veri}\n")

def listeyi_oku(dosya):
    if not os.path.exists(dosya):
        return []
    with open(dosya, "r") as f:
        return [line.strip() for line in f if line.strip()]

@bot.message_handler(content_types=['video'])
def video_kaydet(message):
    file_id = message.video.file_id
    dosya_kaydet(VIDEOLAR_DOSYASI, file_id)
    bot.reply_to(message, "✅ Video hafızaya alındı!")

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = str(message.chat.id)
    kullanicilar = listeyi_oku(KULLANICILAR_DOSYASI)
    if chat_id not in kullanicilar:
        dosya_kaydet(KULLANICILAR_DOSYASI, chat_id)
    bot.reply_to(message, "🚀 Bot aktif! Videoları bana iletirsen listeme eklerim.")

def video_gonder():
    while True:
        time.sleep(60)  # 1 dakikada bir kontrol
        videolar = listeyi_oku(VIDEOLAR_DOSYASI)
        kullanicilar = listeyi_oku(KULLANICILAR_DOSYASI)
        
        if videolar and kullanicilar:
            secilen_video = random.choice(videolar)
            for user_id in kullanicilar:
                try:
                    bot.send_video(chat_id=user_id, video=secilen_video)
                except Exception as e:
                    print("Gönderim hatası:", e)

# Botu ve video döngüsünü arka planda başlatıyoruz
threading.Thread(target=lambda: bot.polling(non_stop=True), daemon=True).start()
threading.Thread(target=video_gonder, daemon=True).start()

# Render'ın port hatası vermemesi için basit web sunucu
class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot calisiyor!")

port = int(os.environ.get("PORT", 10000))
with socketserver.TCPServer(("", port), MyHandler) as httpd:
    httpd.serve_forever()
