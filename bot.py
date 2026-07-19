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
MERCIMEK_VOICE_ID = "CQACAgQAAxkBAAIRpGpdBzb7k9Plsnd2AXVxRCzofIM7AALeHQAC55TpUhWPQyP3j1AaPQQ" 

# --- BAĞLANTILAR ---
bot = telebot.TeleBot(API_TOKEN, threaded=False)
app = Flask(__name__)
bot_running = True 

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client["telegram_bot_db"]
    video_col = db["videolar"]
    user_col = db["kullanicilar"]
    client.admin.command('ping')
    print("🚀 [DEBUG] MongoDB Bağlantısı Başarılı!")
except Exception as e:
    print("❌ [DEBUG] MongoDB Bağlantı Hatası:", e)

def self_ping():
    while True:
        try: requests.get(RENDER_URL)
        except: pass
        time.sleep(300)

@app.route(f'/{API_TOKEN}', methods=['POST'])
def getMessage():
    try:
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        
        # Gelen mesajı loglayalım
        if update.message:
            print(f"📩 [DEBUG] Telegram'dan Mesaj Geldi -> Gönderen ID: {update.message.chat.id} | Metin: {update.message.text}")
        
        bot.process_new_updates([update])
        print("✅ [DEBUG] Mesaj başarıyla process_new_updates'e gönderildi.")
    except Exception as e:
        print("❌ [DEBUG] Webhook Mesaj İşleme Hatası:", e)
    return "!", 200

@app.route("/")
def webhook_status():
    print("🔍 [DEBUG] Webhook durum sayfası tetiklendi (Ping geldi).")
    return "Bot Aktif!", 200

# --- KOMUTLAR ---

@bot.message_handler(commands=['yardim'])
def yardim_menusu(message):
    print(f"⚙️ [DEBUG] /yardim komutu tetiklendi. Tetikleyen: {message.chat.id}")
    yardim_metni = """
🤖 **Semih'in Komut Menüsü:**

🔹 **Genel Komutlar:**
/start - Botu başlatır.
/id - ID numaranı gösterir.
/samih - Samih'e laf atarsın.
/semaver - Semaver muhabbeti.
/doner - Döner durumu.
/ber - ...
/at - ...
/sali - Salı arkadaşım mı?
/baldi - Rastgele replik atar.
/mercimek - Mercimek sesi çalar.
"""
    if str(message.chat.id) == BENIM_ID:
        yardim_metni += """
👑 **Geliştirici Komutları:**
/baslat - Video döngüsünü başlatır.
/durdur - Video döngüsünü durdurur.
/temizle - Havuzu sıfırlar.
/durum - Botun güncel durumunu gösterir.
/kullanicilar - Kayıtlı ID'leri listeler.
/duyuru [mesaj] - Herkese duyuru yapar.
"""
    bot.reply_to(message, yardim_metni, parse_mode="Markdown")

# --- TROL KOMUTLARI ---

@bot.message_handler(commands=['samih'])
def samih_trol(message):
    bot.reply_to(message, "annenmih")

@bot.message_handler(commands=['semaver'])
def semaver_trol(message):
    bot.reply_to(message, "Annenver")

@bot.message_handler(commands=['doner', 'döner'])
def doner_trol(message):
    bot.reply_to(message, "döner çalındı")

@bot.message_handler(commands=['ber'])
def ber_trol(message):
    bot.reply_to(message, "barat")

@bot.message_handler(commands=['at'])
def at_trol(message):
    bot.reply_to(message, "lan at salih")

@bot.message_handler(commands=['salı', 'sali'])
def sali_trol(message):
    print("🤣 [DEBUG] /sali komutu çalıştırıldı!")
    bot.reply_to(message, "benim arkadaşım")

# Özel trol metinleri
@bot.message_handler(func=lambda message: message.text and ("/semih kalp mercimek" in message.text))
def ask_trol(message):
    bot.reply_to(message, "lan aşkımızı karıştırma 0rusbu cocu")

@bot.message_handler(func=lambda message: message.text and ("/selo kalp semih" in message.text))
def selo_trol(message):
    bot.reply_to(message, "SG OE Ü")

# --- SİSTEM KOMUTLARI ---

@bot.message_handler(commands=['id'])
def id_ogren(message):
    bot.reply_to(message, f"Senin ID numaran: {message.chat.id}")

@bot.message_handler(commands=['baslat'])
def baslat(message):
    global bot_running
    if str(message.chat.id) != BENIM_ID: return
    bot_running = True
    bot.reply_to(message, "✅ Döngü başlatıldı!")

@bot.message_handler(commands=['durdur'])
def durdur(message):
    global bot_running
    if str(message.chat.id) != BENIM_ID: return
    bot_running = False
    bot.reply_to(message, "🛑 Döngü durduruldu.")

@bot.message_handler(commands=['baldi'])
def baldi_sozleri(message):
    replikler = ["I HEAR EVERY DOOR YOU OPEN! 📏", "GET OUT WHILE YOU STILL CAN!", "Semih buna kanmaz ahhahaha!", "Welcome to my schoolhouse!"]
    bot.reply_to(message, random.choice(replikler))

@bot.message_handler(commands=['mercimek'])
def mercimek_sesi(message):
    try: bot.send_voice(chat_id=message.chat.id, voice=MERCIMEK_VOICE_ID)
    except: bot.reply_to(message, "Ses dosyasında hata var!")

@bot.message_handler(commands=['temizle'])
def veritabani_temizle(message):
    if str(message.chat.id) != BENIM_ID: return
    silinen = video_col.delete_many({})
    bot.reply_to(message, f"🧹 Havuz sıfırlandı! {silinen.deleted_count} video silindi.")

@bot.message_handler(commands=['durum'])
def bot_durum(message):
    if str(message.chat.id) != BENIM_ID: return
    v_sayi = video_col.count_documents({})
    k_sayi = user_col.count_documents({})
    bot.reply_to(message, f"📊 Durum:\nVideo: {v_sayi}\nKullanıcı: {k_sayi}\nDöngü: {'Çalışıyor' if bot_running else 'Durdu'}")

@bot.message_handler(commands=['kullanicilar'])
def listele_kullanicilar(message):
    if str(message.chat.id) != BENIM_ID: return
    kullanicilar = [doc["chat_id"] for doc in user_col.find()]
    bot.reply_to(message, f"👥 Kullanıcılar:\n" + ("\n".join(kullanicilar) if kullanicilar else "Yok"))

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
    print(f"🚀 [DEBUG] /start basıldı. ID: {message.chat.id}")
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
        if bot_running:
            try:
                aktif_videolar = [doc["file_id"] for doc in video_col.find()]
                aktif_kullanicilar = [doc["chat_id"] for doc in user_col.find()]
                if aktif_videolar and aktif_kullanicilar:
                    secilen_video = random.choice(aktif_videolar)
                    for user_id in aktif_kullanicilar:
                        try: 
                            bot.send_video(chat_id=int(user_id), video=secilen_video, caption="🎬 Semih'ten günün videosu!")
                            print(f"📺 [DEBUG] Arka plan videosu başarıyla gönderildi -> ID: {user_id}")
                        except Exception as ve:
                            print(f"❌ [DEBUG] Video gönderilemedi ({user_id}):", ve)
            except Exception as e:
                print("❌ [DEBUG] Video döngü hatası:", e)

# --- BAŞLANGIÇ AYAĞI ---
if __name__ == "__main__":
    print("⏳ [DEBUG] Webhook ayarlanıyor...")
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=f"{RENDER_URL}/{API_TOKEN}")
    print(f"🔗 [DEBUG] Webhook adresi kuruldu: {RENDER_URL}/{API_TOKEN}")
    
    threading.Thread(target=video_gonder, daemon=True).start()
    threading.Thread(target=self_ping, daemon=True).start()
    print("🧵 [DEBUG] Arka plan thread'leri başlatıldı.")
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
