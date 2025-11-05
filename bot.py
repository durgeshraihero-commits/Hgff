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

# Flask app for web server
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!", 200

@app.route('/health')
def health():
    return "OK", 200

@app.route('/webhook', methods=['POST'])
def webhook():
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
VI) 🔥🔥customised apis for anyone's gallery access (rs200)
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
        # Auto-reply to user
        await message.reply_text("✅ Message received! I will reply to you when I come online. Please be patient...")
    
    elif message.photo:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=user_info)
        await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=message.photo[-1].file_id, caption=message.caption)
        # Auto-reply to user
        await message.reply_text("✅ Photo received! I will check it and reply when I come online.")
    
    elif message.document:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=user_info)
        await context.bot.send_document(chat_id=ADMIN_CHAT_ID, document=message.document.file_id, caption=message.caption)
        # Auto-reply to user
        await message.reply_text("✅ Document received! I will check it and reply when I come online.")

# Admin reply functionality
async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
                    await context.bot.send_message(
                        chat_id=int(user_id),
                        text=update.message.text
                    )
                    await update.message.reply_text("✅ Reply sent successfully!")
                except Exception as e:
                    await update.message.reply_text(f"❌ Failed to send reply: {str(e)}")
    else:
        # If admin sends a command, handle it
        if update.message.text and update.message.text.startswith('/'):
            if update.message.text == '/start':
                await update.message.reply_text("You are admin. All user messages are forwarded to you. Reply to any message to respond to users.")

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception while handling an update: {context.error}")

# Setup bot application
def setup_bot():
    # Check if environment variables are set
    if not BOT_TOKEN or not ADMIN_CHAT_ID:
        logger.error("❌ BOT_TOKEN or ADMIN_CHAT_ID not set in environment variables")
        return None
    
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_admin))
        application.add_handler(MessageHandler(filters.PHOTO | filters.DOCUMENT, forward_to_admin))
        application.add_handler(MessageHandler(filters.ALL, handle_admin_message))
        application.add_error_handler(error_handler)
        
        logger.info("✅ Bot setup completed successfully")
        return application
    except Exception as e:
        logger.error(f"❌ Failed to setup bot: {e}")
        return None

# Run bot using polling
def run_bot():
    logger.info("🔄 Starting bot...")
    application = setup_bot()
    
    if application:
        try:
            # Use polling instead of webhook for simplicity
            application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
        except Exception as e:
            logger.error(f"❌ Bot polling error: {e}")
    else:
        logger.error("❌ Cannot start bot due to setup failure")

# Main function
def main():
    # Validate environment variables
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN environment variable is not set")
        return
    if not ADMIN_CHAT_ID:
        logger.error("❌ ADMIN_CHAT_ID environment variable is not set")
        return
    
    logger.info("🚀 Starting application...")
    
    # Start bot in a separate thread
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("✅ Bot thread started")
    
    # Start Flask app
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🌐 Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    main()
