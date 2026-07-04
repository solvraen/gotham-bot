import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import google.generativeai as genai
from dotenv import load_dotenv

# بارگذاری تنظیمات از فایل .env
load_dotenv()

# دریافت توکن‌ها
TOKEN = os.getenv("TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# تنظیمات جمنای
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# لاگ برای عیب‌یابی
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🦇 گاتهام بیدار است... آماده‌ی شنیدنِ پیام‌های تو هستم.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        response = model.generate_content(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("خطایی در سیستم گاتهام رخ داد.")
        logging.error(f"Error: {e}")

if __name__ == '__main__':
    if not TOKEN or not GEMINI_API_KEY:
        print("خطا: توکن‌ها (TOKEN یا GEMINI_API_KEY) در فایل .env تنظیم نشده‌اند!")
    else:
        application = ApplicationBuilder().token(TOKEN).build()
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("🚀 Gotham Core Online!")
        application.run_polling()
