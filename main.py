import telebot
import requests
from flask import Flask
import threading
import os

# Telegram Bot Setup
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# --- YAHAN AAPKO APNE APP KI DETAILS DAALNI HAIN ---
LOGIN_URL = "https://aapke-app.com/api/login" 
VIDEO_URL_FORMAT = "https://aapke-app.com/api/video/" 
APP_USERNAME = "aapka_email@gmail.com"
APP_PASSWORD = "aapka_password"

def download_video(video_id):
    session = requests.Session()
    
    # Login details
    login_data = {
        'username': APP_USERNAME,
        'password': APP_PASSWORD
    }
    
    try:
        # 1. Login process
        login_response = session.post(LOGIN_URL, data=login_data)
        if login_response.status_code in [200, 201]:
            
            # 2. Video fetch process
            video_url = f"{VIDEO_URL_FORMAT}{video_id}"
            video_response = session.get(video_url, stream=True)
            
            if video_response.status_code == 200:
                filename = f"video_{video_id}.mp4"
                with open(filename, 'wb') as f:
                    for chunk in video_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return filename
            else:
                return "VIDEO_ERROR"
        else:
            return "LOGIN_ERROR"
    except:
        return "NETWORK_ERROR"

# --- TELEGRAM COMMANDS ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello! Main ready hu. Video ID aise bhejein: /video 12345")

@bot.message_handler(commands=['video'])
def handle_video(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "Sahi format: /video 12345")
        return
        
    video_id = parts[1]
    bot.reply_to(message, f"Video {video_id} fetch kar raha hu. Kripya wait karein...")
    
    result = download_video(video_id)
    
    if result == "LOGIN_ERROR":
        bot.reply_to(message, "❌ App login fail ho gaya.")
    elif result == "VIDEO_ERROR":
        bot.reply_to(message, "❌ Video nahi mila.")
    elif result == "NETWORK_ERROR":
        bot.reply_to(message, "❌ Network Error.")
    else:
        bot.reply_to(message, "✅ Video mil gaya! Upload kar raha hu...")
        with open(result, 'rb') as v_file:
            bot.send_video(message.chat.id, v_file)
        os.remove(result) # Server se video delete karna taaki memory full na ho

# --- SERVER KEEP-ALIVE SETUP ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Active!"

def run_bot():
    bot.polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
  
