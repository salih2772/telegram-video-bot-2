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
# Buraya şimdilik 12345 yaz, botu çalıştırınca /id komutuyla gerçek ID'ni öğrenip burayı güncellersin.
BENIM_ID = "12345" 

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

dongu_thread = None

def dongu_kontrol():
    global dongu_thread
    if dongu_thread is None or not dongu_thread.is_alive():
        dongu_thread = threading.Thread(target=video_gonder, daemon=True)
        dongu_thread.start()

def self_ping():
    while True:
        try:
            requests.get(RENDER_URL)
        except Exception as e:
            print("❌ Self-ping hatası:", e)
        time.sleep(300)

@app.route(f'/{API_TOKEN}', methods=['POST'])
def getMessage():
    dongu_kontrol()
    try:
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
    except:
        pass
    return "!", 200

@app.route("/")
def webhook_status():
    dongu_kontrol()
    return "Bot Aktif!", 200

# ID ÖĞRENME KOMUTU
@bot.message_handler(commands=['id'])
def id_ogren(message):
    bot.reply_to(message, f"Senin ID numaran: {message.chat.id}")

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = str(message.chat.id)
    if not user_col.find_one({"chat_id": chat_id}):
        user_col.insert_one({"chat_id": chat_id})
        bot.reply_to(message, "🚀 Bot aktif!")

@bot.message_handler(content_types=['video'])
def video_kaydet(message):
    if str(message.chat.id) != BENIM_ID:
        bot.reply_to(message, "Kanka, sadece geliştirici video ekleyebilir!")
        return

    file_id = message.video.file_id
    if not video_col.find_one({"file_id": file_id}):
        video_col.insert_one({"file_id": file_id})
        bot.reply_to(message, "✅ Video eklendi!")
    else:
        bot.reply_to(message, "Bu video zaten var kanka!")

def video_gonder():
    while True:
        time.sleep(60)
        try:
            aktif_videolar = [doc["file_id"] for doc in video_col.find()]
            aktif_kullanicilar = [doc["chat_id"] for doc in user_col.find()]
            if aktif_videolar and aktif_kullanicilar:
                secilen_video = random.choice(aktif_videolar)
                for user_id in aktif_kullanicilar:
                    try:
                        bot.send_video(chat_id=int(user_id), video=secilen_video, caption="🎬 İşte günün videosu!")
                    except:
                        pass
        except:
            pass

dongu_kontrol()
threading.Thread(target=self_ping, daemon=True).start()

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=f"{RENDER_URL}/{API_TOKEN}")
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
