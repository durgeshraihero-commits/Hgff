import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread
import asyncio

# Load environment variables
from dotenv import load_dotenv
load_dotenv('bot.env')

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask app for web server (required by Render)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!", 200

@app.route('/health')
def health():
    return "OK", 200

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = """
This is my supportbot 
Send any number you want to get details .
Two services are available :-

I) name,father's name,address aadhar number alternate numbers (rs 100)
II) 🔥🔥🔥all that are mentioned above + family members name (rs 150)
III) upi to info 20rs 
IV) number to Facebook 20rs
V) telegram userid to number 20rs
VI) 🔥🔥customised apk for anyone's gallery hack (rs200)
VII)🔥🔥 trace anyone with just a link (rs 20)
VIII) detailed vehicle information (rs 20)
 
This bot is not automated it is manually operated by me so I will reply you when I will come online so be patient...
    """
    await update.message.reply_text(welcome_message)
    
    # Notify admin about new user
    user = update.effective_user
    user_info = f"New user started the bot:\nID: {user.id}\nName: {user.full_name}\nUsername: @{user.username}"
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=user_info)

# Forward all messages to admin
async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message
    
    # Create forward message with user info
    user_info = f"Message from:\nID: {user.id}\nName: {user.full_name}\nUsername: @{user.username}"
    
    if message.text:
        full_message = f"{user_info}\n\nMessage: {message.text}"
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=full_message)
    
    elif message.photo:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=user_info)
        await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=message.photo[-1].file_id, caption=message.caption)
    
    elif message.document:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=user_info)
        await context.bot.send_document(chat_id=ADMIN_CHAT_ID, document=message.document.file_id, caption=message.caption)
    
    # Auto-reply to user
    await message.reply_text("✅ Message received! I will reply to you when I come online. Please be patient...")

# Admin reply functionality
async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != ADMIN_CHAT_ID:
        return
    
    # Check if this is a reply to a forwarded message
    if update.message.reply_to_message:
        replied_message = update.message.reply_to_message
        original_text = replied_message.text
        
        # Extract user ID from the forwarded message
        if "ID:" in original_text:
            lines = original_text.split('\n')
            user_id = None
            for line in lines:
                if line.startswith('ID:'):
                    user_id = line.split(': ')[1]
                    break
            
            if user_id:
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=update.message.text
                    )
                    await update.message.reply_text("✅ Reply sent successfully!")
                except Exception as e:
                    await update.message.reply_text(f"❌ Failed to send reply: {str(e)}")

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception while handling an update: {context.error}")

# Setup bot application
def setup_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_admin))
    application.add_handler(MessageHandler(filters.PHOTO | filters.DOCUMENT, forward_to_admin))
    application.add_handler(MessageHandler(filters.ALL, admin_reply))
    application.add_error_handler(error_handler)
    
    return application

# Run bot in a separate thread
def run_bot():
    application = setup_bot()
    
    # Use webhook for production
    port = int(os.environ.get('PORT', 5000))
    webhook_url = os.environ.get('WEBHOOK_URL', '')
    
    if webhook_url:
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=BOT_TOKEN,
            webhook_url=f"{webhook_url}/{BOT_TOKEN}"
        )
    else:
        # Use polling for development
        application.run_polling()

# Main function
def main():
    # Start bot in a separate thread
    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Start Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main()
