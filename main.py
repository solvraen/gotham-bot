import os
import threading
import logging
import random
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime
import pytz

# --- تنظیمات اولیه ---
load_dotenv()
TOKEN = os.getenv("TOKEN")
GEMINI_API_KEYS = os.getenv("GEMINI_API_KEYS", "").split(",")

# تنظیمات Flask برای زنده ماندن در رندر
app = Flask(__name__)

@app.route('/')
def home():
    return "Gotham Core is Online and Active!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- تنظیمات ربات ---
logging.basicConfig(level=logging.INFO)

def get_persona_prompt():
    hour = datetime.now(pytz.timezone('Asia/Tehran')).hour
    is_bruce = (6 <= hour < 20)
    name = "بروس وین" if is_bruce else "بتمن"
    return f"تو {name} هستی. در گاتهام حضور داری. پاسخ‌هایت باید دقیقاً شخصیت {name} را بازتاب دهد."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    current_key = random.choice(GEMINI_API_KEYS)
    genai.configure(api_key=current_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    try:
        prompt = get_persona_prompt()
        response = model.generate_content(f"{prompt}\nکاربر: {user_text}")
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("سیستم گاتهام دچار اختلال شد.")
        logging.error(f"Error: {e}")

if __name__ == '__main__':
    # اجرای وب‌سرور در یک ترد جداگانه (برای پلن رایگان رندر)
    threading.Thread(target=run_web, daemon=True).start()
    
    # اجرای ربات
    if not TOKEN or not GEMINI_API_KEYS:
        print("خطا: توکن‌ها تنظیم نشده‌اند!")
    else:
        application = ApplicationBuilder().token(TOKEN).build()
        application.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("🦇 گاتهام بیدار است.")))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("🚀 Gotham Core Online!")
        application.run_polling()
