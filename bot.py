import os
import logging
import telebot
from flask import Flask, request
from threading import Thread
from dotenv import load_dotenv

# Load environment variables
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

# Initialize bot and flask app
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot is running and healthy!", 200

@app.route('/health')
def health():
    return "✅ OK", 200

# Store user data for admin replies
user_sessions = {}

# Start command handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
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
    
    bot.reply_to(message, welcome_message)
    
    # Notify admin about new user
    user = message.from_user
    user_info = f"🆕 New user started the bot:\nID: {user.id}\nName: {user.first_name}\nUsername: @{user.username}"
    
    try:
        bot.send_message(ADMIN_CHAT_ID, user_info)
        logger.info(f"New user: {user.id} - {user.first_name}")
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")

# Handle text messages
@bot.message_handler(content_types=['text'])
def handle_text_messages(message):
    user = message.from_user
    user_info = f"💬 Message from:\nID: {user.id}\nName: {user.first_name}\nUsername: @{user.username}"
    
    # Forward message to admin
    try:
        full_message = f"{user_info}\n\n📩 Message: {message.text}"
        sent_msg = bot.send_message(ADMIN_CHAT_ID, full_message)
        
        # Store message info for reply functionality
        user_sessions[sent_msg.message_id] = {
            'user_id': user.id,
            'user_name': user.first_name
        }
        
        # Auto-reply to user
        bot.reply_to(message, "✅ Message received! I will reply to you when I come online. Please be patient...")
        
        logger.info(f"Forwarded message from user {user.id}")
        
    except Exception as e:
        logger.error(f"Error forwarding message: {e}")
        bot.reply_to(message, "❌ Failed to send message. Please try again later.")

# Handle photos
@bot.message_handler(content_types=['photo'])
def handle_photos(message):
    user = message.from_user
    user_info = f"🖼️ Photo from:\nID: {user.id}\nName: {user.first_name}\nUsername: @{user.username}"
    
    try:
        # Send user info to admin
        sent_msg = bot.send_message(ADMIN_CHAT_ID, user_info)
        
        # Forward photo to admin
        bot.send_photo(
            ADMIN_CHAT_ID, 
            message.photo[-1].file_id, 
            caption=message.caption if message.caption else "Photo from user"
        )
        
        # Store message info
        user_sessions[sent_msg.message_id] = {
            'user_id': user.id,
            'user_name': user.first_name
        }
        
        # Auto-reply to user
        bot.reply_to(message, "✅ Photo received! I will check it and reply when I come online.")
        
        logger.info(f"Forwarded photo from user {user.id}")
        
    except Exception as e:
        logger.error(f"Error forwarding photo: {e}")
        bot.reply_to(message, "❌ Failed to send photo. Please try again later.")

# Handle documents
@bot.message_handler(content_types=['document'])
def handle_documents(message):
    user = message.from_user
    user_info = f"📎 Document from:\nID: {user.id}\nName: {user.first_name}\nUsername: @{user.username}"
    
    try:
        # Send user info to admin
        sent_msg = bot.send_message(ADMIN_CHAT_ID, user_info)
        
        # Forward document to admin
        bot.send_document(
            ADMIN_CHAT_ID,
            message.document.file_id,
            caption=message.caption if message.caption else "Document from user"
        )
        
        # Store message info
        user_sessions[sent_msg.message_id] = {
            'user_id': user.id,
            'user_name': user.first_name
        }
        
        # Auto-reply to user
        bot.reply_to(message, "✅ Document received! I will check it and reply when I come online.")
        
        logger.info(f"Forwarded document from user {user.id}")
        
    except Exception as e:
        logger.error(f"Error forwarding document: {e}")
        bot.reply_to(message, "❌ Failed to send document. Please try again later.")

# Admin commands
@bot.message_handler(commands=['admin'])
def admin_commands(message):
    if str(message.from_user.id) != ADMIN_CHAT_ID:
        bot.reply_to(message, "❌ Access denied.")
        return
    
    admin_help = """
🤖 Admin Commands:
/users - Show recent users
/stats - Show bot statistics
/broadcast <message> - Broadcast to all users
"""
    bot.reply_to(message, admin_help)

# Function to handle admin replies manually
def handle_admin_reply(admin_message):
    """
    This function should be called when admin wants to reply to a user.
    You'll implement this based on how you want to handle replies.
    """
    pass

# Run bot polling
def run_bot():
    logger.info("🚀 Starting Telegram bot...")
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found in environment variables")
        return
    
    if not ADMIN_CHAT_ID:
        logger.error("❌ ADMIN_CHAT_ID not found in environment variables")
        return
    
    try:
        logger.info("✅ Bot configured successfully")
        logger.info("🔄 Starting polling...")
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        logger.error(f"❌ Bot polling error: {e}")
        # Restart after delay
        import time
        time.sleep(10)
        run_bot()

# Start bot in a thread
def start_bot():
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("✅ Bot thread started")

# Main function
def main():
    # Validate environment variables
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN environment variable is not set")
        return
    
    if not ADMIN_CHAT_ID:
        logger.error("❌ ADMIN_CHAT_ID environment variable is not set")
        return
    
    logger.info("🎯 Starting application...")
    logger.info(f"🤖 Bot Token: {BOT_TOKEN[:10]}...")
    logger.info(f"👤 Admin ID: {ADMIN_CHAT_ID}")
    
    # Start the bot
    start_bot()
    
    # Start Flask app
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🌐 Starting Flask app on port {port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False
    )

if __name__ == '__main__':
    main()
