import random
import os
import time
import threading
from flask import Flask, request
import telebot
from pymongo import MongoClient

# --- CONFIG ---
API_TOKEN = '8911565294:AAHV62Zuwq9TOvKY2Nn6anRhDRXgP0hlfZc'
MONGO_URI = "mongodb+srv://darbesalih31_db_user:Salih123456@cluster0.xaa391s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0" 
RENDER_URL = "https://telegram-video-bot-2-1.onrender.com"

# --- BAĞLANTILAR ---
bot = telebot.TeleBot(API_TOKEN, threaded=False)
app = Flask(__name__)

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client["telegram_bot_db"]
    video_col = db["videolar"]
    user_col = db["kullanicilar"]
    client.admin.command('ping')
    print("🚀 MongoDB Bağlantısı Başarılı!")
except Exception as e:
    print("❌ MongoDB Bağlantı Hatası:", e)

# Arka plan döngüsünün canlı olup olmadığını kontrol eden değişken
dongu_thread = None

def dongu_kontrol():
    global dongu_thread
    if dongu_thread is None or not dongu_thread.is_alive():
        print("⚠️ Arka plan döngüsü durmuş veya başlamamış! Yeniden başlatılıyor...")
        dongu_thread = threading.Thread(target=video_gonder, daemon=True)
        dongu_thread.start()

# --- WEBHOOK GİRİŞ NOKTASI ---
@app.route(f'/{API_TOKEN}', methods=['POST'])
def getMessage():
    dongu_kontrol()  # Her istek geldiğinde döngü yaşıyor mu diye bak, öldüyse dirilt
    try:
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
    except Exception as e:
        print("Webhook güncelleme işleme hatası:", e)
    return "!", 200

@app.route("/")
def webhook_status():
    dongu_kontrol()  # Siteye her ping geldiğinde döngüyü kontrol et
    return "Bot Webhook Modunda Aktif ve Dinlemede!", 200

# --- BOT KOMUTLARI ---
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = str(message.chat.id)
    try:
        if not user_col.find_one({"chat_id": chat_id}):
            user_col.insert_one({"chat_id": chat_id})
            bot.reply_to(message, "🚀 Bot aktif! Kanalındaki videoları bana yönlendir, sırayla paylaşayım.")
        else:
            bot.reply_to(message, "Zaten aktifsin kanka! Videoları göndermeye devam edebilirsin.")
    except Exception as e:
        print("Kullanıcı kaydetme hatası:", e)
        bot.reply_to(message, "Şu an veritabanına bağlanamıyorum kanka, birazdan tekrar dene.")

@bot.message_handler(content_types=['video'])
def video_kaydet(message):
    file_id = message.video.file_id
    try:
        if not video_col.find_one({"file_id": file_id}):
            video_col.insert_one({"file_id": file_id})
            toplam_video = video_col.count_documents({})
            bot.reply_to(message, f"✅ Video güvenli bulut hafızasına alındı! Toplam video sayısı: {toplam_video}")
        else:
            bot.reply_to(message, "Bu video zaten hafızada var kanka!")
    except Exception as e:
        print("Video kaydetme hatası:", e)

# --- ARKA PLAN VİDEO GÖNDERİM DÖNGÜSÜ ---
def video_gonder():
    while True:
        time.sleep(60)  # Kanka buraya kesinlikle dokunmadım, senin 60 saniyelik test süren aynen duruyor
        try:
            aktif_videolar = [doc["file_id"] for doc in video_col.find()]
            aktif_kullanicilar = [doc["chat_id"] for doc in user_col.find()]
            
            if aktif_videolar and aktif_kullanicilar:
                secilen_video = random.choice(aktif_videolar)
                for user_id in aktif_kullanicilar:
                    try:
                        bot.send_video(chat_id=int(user_id), video=secilen_video, caption="🎬 İşte günün videosu!")
                    except Exception as e:
                        print(f"Gönderim hatası (User ID: {user_id}):", e)
        except Exception as e:
            print("Döngü içinde MongoDB hatası:", e)

# İlk açılışta döngüyü tetikliyoruz
dongu_kontrol()

# --- RUN ---
if __name__ == "__main__":
    try:
        bot.remove_webhook()
        time.sleep(1)
        bot.set_webhook(url=f"{RENDER_URL}/{API_TOKEN}")
        print("✅ Telegram Webhook başarıyla ayarlandı!")
    except Exception as e:
        print("❌ Webhook ayarlama hatası:", e)

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
