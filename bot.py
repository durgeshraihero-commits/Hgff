import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Load token from Render environment variable
TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I am alive on Render 🚀")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Commands:\n/start - Greeting\n/help - Show this help")

def main():
    # Build app (no Updater inside!)
    app = Application.builder().token(TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Run bot
    app.run_polling()

if __name__ == "__main__":
    main()
