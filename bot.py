from telegram.ext import Application, CommandHandler

BOT_TOKEN = "8307999302:AAFk0WOKT_6tzuDs0h4FvGtpnMiguecj54Q"

async def start(update, context):
    await update.message.reply_text("Hello! Bot is working.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
