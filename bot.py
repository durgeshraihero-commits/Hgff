import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from flask import Flask
from threading import Thread
import time

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

# Flask app for web server
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!", 200

@app.route('/health')
def health():
    return "OK", 200

# Start command handler
def start(update: Update, context: CallbackContext):
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
    update.message.reply_text(welcome_message)
    
    # Notify admin about new user
    user = update.effective_user
    user_info = f"New user started the bot:\nID: {user.id}\nName: {user.full_name}\nUsername: @{user.username}"
    context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=user_info)

# Forward all messages to admin
def forward_to_admin(update: Update, context: CallbackContext):
    user = update.effective_user
    message = update.message
    
    # Create forward message with user info
    user_info = f"Message from:\nID: {user.id}\nName: {user.full_name}\nUsername: @{user.username}"
    
    if message.text:
        full_message = f"{user_info}\n\nMessage: {message.text}"
        context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=full_message)
    
    elif message.photo:
        context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=user_info)
        context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=message.photo[-1].file_id, caption=message.caption)
    
    elif message.document:
        context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=user_info)
        context.bot.send_document(chat_id=ADMIN_CHAT_ID, document=message.document.file_id, caption=message.caption)
    
    # Auto-reply to user
    update.message.reply_text("✅ Message received! I will reply to you when I come online. Please be patient...")

# Admin reply functionality
def admin_reply(update: Update, context: CallbackContext):
    if str(update.effective_user.id) != ADMIN_CHAT_ID:
        return
    
    # Check if this is a reply to a forwarded message
    if update.message.reply_to_message:
        replied_message = update.message.reply_to_message
        original_text = replied_message.text
        
        # Extract user ID from the forwarded message
        if original_text and "ID:" in original_text:
            lines = original_text.split('\n')
            user_id = None
            for line in lines:
                if line.startswith('ID:'):
                    user_id = line.split(': ')[1]
                    break
            
            if user_id:
                try:
                    context.bot.send_message(
                        chat_id=user_id,
                        text=update.message.text
                    )
                    update.message.reply_text("✅ Reply sent successfully!")
                except Exception as e:
                    update.message.reply_text(f"❌ Failed to send reply: {str(e)}")

# Error handler
def error_handler(update: Update, context: CallbackContext):
    logger.error(f"Exception while handling an update: {context.error}")

# Setup bot
def setup_bot():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    # Add handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, forward_to_admin))
    dispatcher.add_handler(MessageHandler(Filters.photo | Filters.document, forward_to_admin))
    dispatcher.add_handler(MessageHandler(Filters.all, admin_reply))
    dispatcher.add_error_handler(error_handler)
    
    return updater

# Run bot in background
def run_bot():
    updater = setup_bot()
    
    # Start polling
    updater.start_polling()
    logger.info("Bot started polling...")
    
    # Run the bot until interrupted
    updater.idle()

# Main function
def main():
    # Check if environment variables are set
    if not BOT_TOKEN or not ADMIN_CHAT_ID:
        logger.error("BOT_TOKEN or ADMIN_CHAT_ID not set in environment variables")
        return
    
    # Start bot in a separate thread
    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    logger.info("Bot thread started")
    
    # Start Flask app
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    main()
