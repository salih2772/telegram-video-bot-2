import random
import telebot
import os
import time
import threading

API_TOKEN = '8911565294:AAHV62Zuwq9TOvKY2Nn6anRhDRXgP0hlfZc'
bot = telebot.TeleBot(API_TOKEN)

KANAL_ID = -1004367140777
KULLANICILAR_DOSYASI = "kullanicilar.txt"
son_gonderilen_mesaj_id = None

def kullanicilari_yukle():
    if not os.path.exists(KULLANICILAR_DOSYASI): return []
    with open(KULLANICILAR_DOSYASI, "r") as f:
        return [line.strip() for line in f if line.strip()]

def video_gonder():
    global son_gonderilen_mesaj_id
    while True:
        time.sleep(60)
        kullanicilar = kullanicilari_yukle()
        if not kullanicilar: continue

        try:
            history = bot.get_chat_history(chat_id=KANAL_ID, limit=100)
            videolu_mesajlar = [msg for msg in history if msg.video is not None]
            
            if not videolu_mesajlar:
                continue

            if len(videolu_mesajlar) > 1 and son_gonderilen_mesaj_id is not None:
                secenekler = [msg for msg in videolu_mesajlar if msg.message_id != son_gonderilen_mesaj_id]
            else:
                secenekler = videolu_mesajlar

            secilen_mesaj = random.choice(secenekler)
            son_gonderilen_mesaj_id = secilen_mesaj.message_id
            
            for user_id in kullanicilar:
                try:
                    bot.send_video(chat_id=user_id, video=secilen_mesaj.video.file_id, caption="🎬 İşte yeni video!")
                except:
                    pass
        except Exception as e:
            print("Hata:", e)

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = str(message.chat.id)
    kullanicilar = kullanicilari_yukle()
    if chat_id not in kullanicilar:
        with open(KULLANICILAR_DOSYASI, "a") as f:
            f.write(f"{chat_id}\n")
    bot.reply_to(message, "Ölümsüz Bulut Botu Aktif! 🚀")

threading.Thread(target=lambda: bot.polling(non_stop=True), daemon=True).start()
threading.Thread(target=video_gonder, daemon=True).start()

# Render'ın ücretsiz portunu açık tutmak için web sunucusu
import http.server
import socketserver
class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot calisiyor!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    with socketserver.TCPServer(("", port), MyHandler) as httpd:
        httpd.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

while True:
    time.sleep(100)
