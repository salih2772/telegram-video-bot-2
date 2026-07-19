import random
import os
import time
import threading
import requests
from flask import Flask, request
import telebot
from pymongo import MongoClient

# --- CONFIG ---
API_TOKEN = '8911565294:AAHV62Zuwq9TOvKY2Nn6anRhDRXgP0hlfZc'
MONGO_URI = "mongodb+srv://darbesalih31_db_user:Salih123456@cluster0.xaa391s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0" 
RENDER_URL = "https://telegram-video-bot-2-1.onrender.com"
BENIM_ID = "7826173288" 
# Mercimek sesi ID'sini buraya yapıştıracaksın (bota atınca sana ID'yi verecek)
MERCIMEK_VOICE_ID = "BURAYA_KODU_YAPISTIR" 

# --- BAĞLANTILAR ---
bot = telebot.TeleBot(API_TOKEN, threaded=False)
app = Flask(__name__)
bot_running = True # Döngü kontrolü için

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client["telegram_bot_db"]
    video_col = db["videolar"]
    user_col = db["kullanicilar"]
    client.admin.command('ping')
    print("🚀 MongoDB Bağlantısı Başarılı!")
except Exception as e:
    print("❌ MongoDB Bağlantı Hatası:", e)

# ... (Döngü ve Webhook fonksiyonları aynı kalıyor) ...
dongu_thread = None
def dongu_kontrol():
    global dongu_thread
    if dongu_thread is None or not dongu_thread.is_alive():
        dongu_thread = threading.Thread(target=video_gonder, daemon=True)
        dongu_thread.start()

def self_ping():
    while True:
        try: requests.get(RENDER_URL)
        except: pass
        time.sleep(300)

@app.route(f'/{API_TOKEN}', methods=['POST'])
def getMessage():
    dongu_kontrol()
    try:
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
    except: pass
    return "!", 200

@app.route("/")
def webhook_status():
    dongu_kontrol()
    return "Bot Aktif!", 200

# --- KOMUTLAR ---

@bot.message_handler(commands=['baslat'])
def baslat(message):
    global bot_running
    if str(message.chat.id) != BENIM_ID: return
    bot_running = True
    bot.reply_to(message, "✅ Döngü başlatıldı, videolar akmaya devam!")

@bot.message_handler(commands=['durdur'])
def durdur(message):
    global bot_running
    if str(message.chat.id) != BENIM_ID: return
    bot_running = False
    bot.reply_to(message, "🛑 Döngü durduruldu. Sadece komutlara bakıyorum.")

@bot.message_handler(commands=['baldi'])
def baldi_sozleri(message):
    replikler = ["I HEAR EVERY DOOR YOU OPEN! 📏", "GET OUT WHILE YOU STILL CAN!", "Semih buna kanmaz ahhahaha!", "Welcome to my schoolhouse!"]
    bot.reply_to(message, random.choice(replikler))

@bot.message_handler(commands=['mercimek'])
def mercimek_sesi(message):
    if MERCIMEK_VOICE_ID == "BURAYA_KODU_YAPISTIR":
        bot.reply_to(message, "Kanka önce ses dosyasını bota atıp ID'sini öğrenmen lazım, koda işlemedin!")
    else:
        bot.send_voice(chat_id=message.chat.id, voice=MERCIMEK_VOICE_ID)

# Ses dosyası ID'sini bulmak için yardımcı
@bot.message_handler(content_types=['voice', 'audio'])
def ses_id_bul(message):
    if str(message.chat.id) == BENIM_ID:
        ses_id = message.voice.file_id if message.voice else message.audio.file_id
        bot.reply_to(message, f"🎯 Ses dosyasının ID'si: `{ses_id}`\n\nBunu koddaki MERCIMEK_VOICE_ID kısmına yapıştır!")

# --- DİĞER FONKSİYONLAR ---
# (Temizle, durum, kullanicilar, start, video_kaydet aynı kalıyor...)

@bot.message_handler(commands=['temizle'])
def veritabani_temizle(message):
    if str(message.chat.id) != BENIM_ID:
        bot.reply_to(message, "Semih buna kanmaz ahhahaha!")
        return
    silinen = video_col.delete_many({})
    bot.reply_to(message, f"🧹 Havuz sıfırlandı! {silinen.deleted_count} video silindi.")

@bot.message_handler(commands=['durum'])
def bot_durum(message):
    if str(message.chat.id) != BENIM_ID: return
    video_sayisi = video_col.count_documents({})
    kullanici_sayisi = user_col.count_documents({})
    bot.reply_to(message, f"📊 Semih'in Durumu:\n- Video: {video_sayisi}\n- Kullanıcı: {kullanici_sayisi}\n- Durum: {'Çalışıyor' if bot_running else 'Durdu'}")

@bot.message_handler(commands=['kullanicilar'])
def listele_kullanicilar(message):
    if str(message.chat.id) != BENIM_ID: return
    kullanicilar = [doc["chat_id"] for doc in user_col.find()]
    liste = "\n".join(kullanicilar) if kullanicilar else "Yok."
    bot.reply_to(message, f"👥 Kullanıcılar:\n{liste}")

@bot.message_handler(commands=['duyuru'])
def toplu_duyuru(message):
    if str(message.chat.id) != BENIM_ID: return
    duyuru_metni = message.text.replace("/duyuru", "").strip()
    kullanicilar = [doc["chat_id"] for doc in user_col.find()]
    for user_id in kullanicilar:
        try: bot.send_message(chat_id=int(user_id), text=f"📢 {duyuru_metni}")
        except: pass
    bot.reply_to(message, "✅ Duyuru gönderildi!")

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = str(message.chat.id)
    if not user_col.find_one({"chat_id": chat_id}):
        user_col.insert_one({"chat_id": chat_id})
        bot.reply_to(message, "🚀 Semih aktif!")

@bot.message_handler(content_types=['video'])
def video_kaydet(message):
    if str(message.chat.id) != BENIM_ID: return
    file_id = message.video.file_id
    if not video_col.find_one({"file_id": file_id}):
        video_col.insert_one({"file_id": file_id})
        bot.reply_to(message, "✅ Video eklendi!")

def video_gonder():
    while True:
        time.sleep(60)
        if bot_running: # Sadece bot_running True ise çalışır
            try:
                aktif_videolar = [doc["file_id"] for doc in video_col.find()]
                aktif_kullanicilar = [doc["chat_id"] for doc in user_col.find()]
                if aktif_videolar and aktif_kullanicilar:
                    secilen_video = random.choice(aktif_videolar)
                    for user_id in aktif_kullanicilar:
                        try: bot.send_video(chat_id=int(user_id), video=secilen_video, caption="🎬 Semih'ten günün videosu!")
                        except: pass
            except: pass

dongu_kontrol()
threading.Thread(target=self_ping, daemon=True).start()

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=f"{RENDER_URL}/{API_TOKEN}")
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
