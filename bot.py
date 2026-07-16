import random
import os
import time
import threading
from flask import Flask, request
import telebot
from pymongo import MongoClient

# --- CONFIG ---
API_TOKEN = '8911565294:AAHV62Zuwq9TOvKY2Nn6anRhDRXgP0hlfZc'
MONGO_URI = "mongodb+srv://darbesalih31_db_user:3JA3BdQ9AO1JSkSu@cluster0.xaa391s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0" 

# --- BAĞLANTILAR ---
bot = telebot.TeleBot(API_TOKEN, threaded=False)
app = Flask(__name__)

# MongoDB Bağlantısı
client = MongoClient(MONGO_URI)
db = client["telegram_bot_db"]
video_col = db["videolar"]
user_col = db["kullanicilar"]

# --- WEBHOOK GİRİŞ NOKTASI ---
@app.route(f'/{API_TOKEN}', methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook_status():
    return "Bot Webhook Modunda Aktif!", 200

# --- BOT KOMUTLARI ---
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = str(message.chat.id)
    
    # Kullanıcı zaten kayıtlı mı kontrol et, yoksa kaydet
    if not user_col.find_one({"chat_id": chat_id}):
        user_col.insert_one({"chat_id": chat_id})
        bot.reply_to(message, "🚀 Bot aktif! Kanalındaki videoları bana yönlendir, sırayla paylaşayım.")
    else:
        bot.reply_to(message, "Zaten aktifsin kanka! Videoları göndermeye devam edebilirsin.")

@bot.message_handler(content_types=['video'])
def video_kaydet(message):
    file_id = message.video.file_id
    
    # Video zaten kayıtlı mı kontrol et, yoksa kaydet
    if not video_col.find_one({"file_id": file_id}):
        video_col.insert_one({"file_id": file_id})
        toplam_video = video_col.count_documents({})
        bot.reply_to(message, f"✅ Video güvenli bulut hafızasına alındı! Toplam video sayısı: {toplam_video}")
    else:
        bot.reply_to(message, "Bu video zaten hafızada var kanka!")

# --- ARKA PLAN VİDEO GÖNDERİM DÖNGÜSÜ ---
def video_gonder():
    while True:
        time.sleep(60)  # Her 60 saniyede bir kontrol et ve gönder
        
        # Veritabanından güncel verileri çekiyoruz
        aktif_videolar = [doc["file_id"] for doc in video_col.find()]
        aktif_kullanicilar = [doc["chat_id"] for doc in user_col.find()]
        
        if aktif_videolar and aktif_kullanicilar:
            secilen_video = random.choice(aktif_videolar)
            for user_id in aktif_kullanicilar:
                try:
                    bot.send_video(chat_id=int(user_id), video=secilen_video, caption="🎬 İşte günün videosu!")
                except Exception as e:
                    print("Gönderim hatası (Kullanıcı botu engellemiş olabilir):", e)

# Video gönderme döngüsünü arka planda başlatıyoruz
threading.Thread(target=video_gonder, daemon=True).start()

# --- RUN ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
