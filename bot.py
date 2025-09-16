from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Send greeting and a button with the webapp link that includes the user chat_id
    """
    user_chat_id = update.effective_chat.id
    webapp_with_id = f"{WEBAPP_URL}?chat_id={user_chat_id}"

    keyboard = [[InlineKeyboardButton("📸 Open Camera App", url=webapp_with_id)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 Hello! I’m your Camera Bot.\n\n"
        "Click the button below to open the camera app and capture your photos.",
        reply_markup=reply_markup
    )

def main():
    """
    Run the bot
    """
    if not BOT_TOKEN:
        raise ValueError("❌ BOT_TOKEN is missing! Add it to your .env file.")
    if not WEBAPP_URL:
        raise ValueError("❌ WEBAPP_URL is missing! Add it to your .env file.")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    print("🤖 Bot is running... Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()
