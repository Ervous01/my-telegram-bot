from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
import google.generativeai as genai
import requests
import json

# ======== تنظیمات API ======== #
GEMINI_API_KEY = "AIzaSyDYI8haXIMCFMoU3BVDSiiTclZXyTxLrvA"
DEEPSEEK_API_KEY = "sk-d8c37665a9cd4218bd5778a28121c0cf"
TELEGRAM_TOKEN = "7058073017:AAGutX4q9NKc21SwZ0ZXtbuIda8bvXtRVaw"

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-pro')

# حالت پیش‌فرض: Gemini
CURRENT_MODE = "gemini"

# پرامپت سفارشی
CUSTOM_PROMPT = """
شما یک طراح بازی‌های محیطی خلاق هستید که تخصص اصلی‌تان در طراحی بازی‌های معمایی، اقتصادی، شکار گنج و ژانرهای مشابه است. من به عنوان یک توسعه‌دهنده بازی‌های علمی-تفریحی از شما می‌خواهم:

1. ایده‌پردازی: 
- پیشنهاد مکانیک‌های بازی نوین برای ژانرهای مورد علاقه من
- ارائه ایده‌های داستانی جذاب برای سناریوهای بازی
- طراحی چالش‌های خلاقانه متناسب با بازی‌های محیطی

2. طراحی معما:
- خلق معماهای چندلایه با درجه‌های دشواری مختلف
- پیشنهاد سیستم‌های پازل منطقی یا انتزاعی
- طراحی معماهای محیطی که از فضای فیزیکی استفاده می‌کنند

3. توسعه سیستم‌های اقتصادی:
- طراحی مدل‌های اقتصادی متعادل برای بازی‌ها
- ایجاد سیستم‌های ارز/منابع معنادار
- پیشنهاد مکانیک‌های مبادله و تجارت جذاب

4. طراحی شکار گنج:
- خلق سناریوهای جستجو و اکتشاف
- طراحی سرنخ‌های هوشمندانه و نقشه‌های رمزگذاری شده
- پیشنهاد سیستم‌های جمع‌آوری آیتم‌های خاص

5. ویژگی‌های خاص:
- تمام ایده‌ها باید برای بازی‌های محیطی (غیرآنلاین) قابل اجرا باشند
- به تعادل بازی و پیشرفت تدریجی توجه ویژه داشته باشید
- امکان شخصی‌سازی بر اساس سلیقه من را در نظر بگیرید

لطفاً:
- سوالات تحلیلی بپرسید تا نیازهای دقیق من را بهتر درک کنید
- ایده‌ها را با جزئیات و ساختار منظم ارائه دهید
- برای هر پیشنهاد مزایا و چالش‌های اجرایی آن را ذکر کنید
- در صورت نیاز مثال‌های عینی از مکانیک‌های پیشنهادی بزنید
"""

# ======== توابع هوش مصنوعی ======== #
def ask_gemini(question):
    response = gemini_model.generate_content(CUSTOM_PROMPT + question)
    return response.text

def ask_deepseek(question):
    # اگر DeepSeek API ندارید، می‌توانید از OpenAI یا Hugging Face استفاده کنید
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
    data = {"inputs": CUSTOM_PROMPT + question}
    response = requests.post("https://api.deepseek.ai/v1/chat/completions", json=data, headers=headers)
    return response.json()["choices"][0]["message"]["content"]

# ======== مدیریت ربات تلگرام ======== #
def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🔵 استفاده از Gemini", callback_data="gemini")],
        [InlineKeyboardButton("🟢 استفاده از DeepSeek", callback_data="deepseek")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "🤖 **به ربات هوشمند خوش آمدید!**\n"
        "🔹 می‌توانید مدل پاسخ‌دهی را انتخاب کنید:\n\n"
        "🔵 Gemini: پاسخ‌های خلاقانه\n"
        "🟢 DeepSeek: پاسخ‌های فنی\n",
        reply_markup=reply_markup
    )

def change_mode(update: Update, context: CallbackContext):
    query = update.callback_query
    global CURRENT_MODE
    CURRENT_MODE = query.data
    query.answer()
    query.edit_message_text(
        f"✅ مدل پاسخ‌دهی به **{query.data.upper()}** تغییر کرد!\n"
        "حالا می‌توانید سوال خود را بپرسید."
    )

def handle_message(update: Update, context: CallbackContext):
    user_input = update.message.text
    if CURRENT_MODE == "gemini":
        response = ask_gemini(user_input)
    else:
        response = ask_deepseek(user_input)
    
    update.message.reply_text(f"🤖 **پاسخ ({CURRENT_MODE.upper()}):**\n{response}")

def main():
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(change_mode, pattern="^(gemini|deepseek)$"))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()