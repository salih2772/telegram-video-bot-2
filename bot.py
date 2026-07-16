import random
import telebot
import os
import time
import threading
import http.server
import socketserver

API_TOKEN = '8911565294:AAHV62Zuwq9TOvKY2Nn6anRhDRXgP0hlfZc'
bot = telebot.TeleBot(API_TOKEN)

# Verileri dosya yerine doğrudan canlı hafızada (RAM) tutuyoruz!
AKTIF_VIDEOLAR = []
AKTIF_KULLANICILAR = set()

@bot.message_handler(content_types=['video'])
def video_kaydet(message):
    file_id = message.video.file_id
    if file_id not in AKTIF_VIDEOLAR:
        AKTIF_VIDEOLAR.append(file_id)
    bot.reply_to(message, f"✅ Video hafızaya alındı! Toplam video sayısı: {len(AKTIF_VIDEOLAR)}")

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = str(message.chat.id)
    AKTIF_KULLANICILAR.add(chat_id)
    bot.reply_to(message, "🚀 Bot aktif! Kanalındaki videoları bana yönlendir (forward et), onları hafızama alıp sırayla paylaşayım.")

def video_gonder():
    while True:
        time.sleep(60)  # Her 60 saniyede bir gönderim yapar
        
        # Eğer hafızada video ve kullanıcı varsa gönderim başlar
        if AKTIF_VIDEOLAR and AKTIF_KULLANICILAR:
            secilen_video = random.choice(AKTIF_VIDEOLAR)
            for user_id in list(AKTIF_KULLANICILAR):
                try:
                    bot.send_video(chat_id=int(user_id), video=secilen_video, caption="🎬 İşte günün videosu!")
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
