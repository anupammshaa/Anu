import telebot
import requests
from flask import Flask
import threading
import os

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Aapka asli Classplus API Link (contentId ke aage ka hissa user chat se dega)
VIDEO_URL_FORMAT = "https://api.classplusapp.com/cams/uploader/video/jw-signed-url?contentId=" 

user_data = {}

# --- 1. START COMMAND ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome Anupam bhai! 👋\nClassplus app se video link nikalne ke liye bot ready hai.\nSabse pehle apna Token save karne ke liye dabayein 👉 /login")

# --- 2. TOKEN SUBMIT KARNA ---
@bot.message_handler(commands=['login'])
def ask_token(message):
    msg = bot.reply_to(message, "Kripya PC ke Network tab se nikala gaya lamba wala **x-access-token** yahan paste karein:")
    bot.register_next_step_handler(msg, save_token)

def save_token(message):
    chat_id = message.chat.id
    user_data[chat_id] = message.text # Token save kar liya
    
    # Security ke liye token delete karna
    try:
        bot.delete_message(chat_id, message.message_id)
    except:
        pass
        
    bot.reply_to(message, "✅ Token successfully save ho gaya! \nAb aap video ki ID bhej sakte hain. \nExample: `/video U2FsdGV...` (video ka lamba encrypted ID)")

# --- 3. VIDEO FETCH PROCESS (.m3u8 link nikalna) ---
@bot.message_handler(commands=['video'])
def handle_video(message):
    chat_id = message.chat.id
    
    if chat_id not in user_data:
        bot.reply_to(message, "⚠️ Pehle aapko apna Token dalna hoga! Kripya `/login` par click karein.")
        return

    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "Sahi format use karein: `/video [Video_ID_Code]`")
        return
        
    video_id = parts[1]
    bot.reply_to(message, "Aapke Token se video ka link dhoondh raha hu. Wait karein...")
    
    my_token = user_data[chat_id]
    
    # Classplus header format
    headers = {
        'x-access-token': my_token
    }
    
    video_url = f"{VIDEO_URL_FORMAT}{video_id}"
    
    try:
        # API request
        api_response = requests.get(video_url, headers=headers)
        
        if api_response.status_code == 200:
            data = api_response.json()
            
            # API ke answer me se "url" wala hissa nikalna
            if "url" in data:
                m3u8_link = data["url"]
                bot.reply_to(message, f"✅ **SUCCESS! Video Link Mil Gaya:**\n\n`{m3u8_link}`\n\nIs link ko copy karke aap 1DM app, VLC Player, ya kisi bhi m3u8 downloader me daal kar video dekh ya download kar sakte hain.")
            else:
                bot.reply_to(message, "⚠️ API ne data bheja par usme 'url' nahi mila. Sayad Token valid nahi hai.")
        else:
            bot.reply_to(message, f"❌ Error: Sayad Token expire ho gaya hai ya Video ID galat hai. (Status Code: {api_response.status_code})")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Server ya Network Error: {e}")

# --- SERVER KEEP-ALIVE ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Active!"

def run_bot():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
                
