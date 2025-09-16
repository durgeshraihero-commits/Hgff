import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Put your bot token here (or set as environment variable BOT_TOKEN)
TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")


# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I am alive on Render!")


# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Available commands:\n/start - Greet\n/help - Show this help\n/echo <text> - Repeat your text")


# /echo command
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        await update.message.reply_text(" ".join(context.args))
    else:
        await update.message.reply_text("Usage: /echo <text>")


def main():
    # Build the bot application
    app = Application.builder().token(TOKEN).build()

    # Register commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("echo", echo))

    # Run the bot
    app.run_polling()


if __name__ == "__main__":
    main()
