import os
import logging
import telebot
from flask import Flask
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

# Store user data for replies
user_messages = {}
# Track if bot is already running
bot_running = False

@app.route('/')
def home():
    return "🤖 Bot is running and healthy!", 200

@app.route('/health')
def health():
    return "✅ OK", 200

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
        logger.info(f"✅ Notified admin about new user: {user.id}")
    except Exception as e:
        logger.error(f"❌ Failed to notify admin: {e}")

# Handle all user messages
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'document'])
def handle_all_messages(message):
    # Ignore commands from users (only process admin commands separately)
    if message.text and message.text.startswith('/') and str(message.from_user.id) != ADMIN_CHAT_ID:
        return
        
    user = message.from_user
    message_id = message.message_id
    
    # Store user info
    user_messages[message_id] = {
        'user_id': user.id,
        'user_name': user.first_name,
        'username': user.username
    }
    
    logger.info(f"📨 Processing message #{message_id} from user {user.id}")
    
    # If message is from admin and is a command, handle separately
    if str(message.from_user.id) == ADMIN_CHAT_ID and message.text and message.text.startswith('/'):
        return  # Let the command handlers deal with it
    
    # Forward user messages to admin
    if message.text:
        forward_text_message(message, message_id)
    elif message.photo:
        forward_photo_message(message, message_id)
    elif message.document:
        forward_document_message(message, message_id)

def forward_text_message(message, message_id):
    user = message.from_user
    user_info = f"💬 Message #{message_id}\nFrom: {user.first_name}\nUsername: @{user.username}\nUser ID: {user.id}"
    
    try:
        # Send to admin
        admin_message = f"{user_info}\n\n📩 Message:\n{message.text}\n\n💡 To reply, use:\n/reply {message_id} your_message"
        sent = bot.send_message(ADMIN_CHAT_ID, admin_message)
        logger.info(f"✅ Text forwarded to admin. Admin message ID: {sent.message_id}")
        
        # Auto-reply to user
        bot.reply_to(message, "✅ Message received! I will reply to you when I come online. Please be patient...")
        
    except Exception as e:
        logger.error(f"❌ Error forwarding text: {e}")

def forward_photo_message(message, message_id):
    user = message.from_user
    user_info = f"🖼️ Photo #{message_id}\nFrom: {user.first_name}\nUsername: @{user.username}\nUser ID: {user.id}"
    
    try:
        caption = message.caption if message.caption else "No caption"
        admin_message = f"{user_info}\n\n📸 Caption: {caption}\n\n💡 To reply, use:\n/reply {message_id} your_message"
        
        bot.send_message(ADMIN_CHAT_ID, admin_message)
        bot.send_photo(ADMIN_CHAT_ID, message.photo[-1].file_id)
        logger.info(f"✅ Photo forwarded to admin")
        
        bot.reply_to(message, "✅ Photo received! I will check it and reply soon.")
        
    except Exception as e:
        logger.error(f"❌ Error forwarding photo: {e}")

def forward_document_message(message, message_id):
    user = message.from_user
    user_info = f"📎 Document #{message_id}\nFrom: {user.first_name}\nUsername: @{user.username}\nUser ID: {user.id}"
    
    try:
        caption = message.caption if message.caption else "No caption"
        admin_message = f"{user_info}\n\n📄 Caption: {caption}\n\n💡 To reply, use:\n/reply {message_id} your_message"
        
        bot.send_message(ADMIN_CHAT_ID, admin_message)
        bot.send_document(ADMIN_CHAT_ID, message.document.file_id)
        logger.info(f"✅ Document forwarded to admin")
        
        bot.reply_to(message, "✅ Document received! I will check it and reply soon.")
        
    except Exception as e:
        logger.error(f"❌ Error forwarding document: {e}")

# Admin reply command
@bot.message_handler(commands=['reply'])
def admin_reply(message):
    logger.info(f"🔄 Admin reply attempt from user {message.from_user.id}")
    
    # Check if user is admin
    if str(message.from_user.id) != ADMIN_CHAT_ID:
        bot.reply_to(message, "❌ Access denied. Admin only.")
        return
    
    try:
        # Parse command: /reply MESSAGE_ID Your reply text
        parts = message.text.split(' ', 2)
        if len(parts) < 3:
            bot.reply_to(message, "❌ Usage: /reply MESSAGE_ID Your message here\nExample: /reply 320 Hello! How can I help?")
            return
        
        original_message_id = int(parts[1])
        reply_text = parts[2]
        
        logger.info(f"🔍 Looking for message ID: {original_message_id}")
        
        # Get user info from stored messages
        if original_message_id not in user_messages:
            recent_ids = list(user_messages.keys())[-5:] if user_messages else "No recent messages"
            bot.reply_to(message, f"❌ Message ID {original_message_id} not found. Recent IDs: {recent_ids}")
            return
        
        user_info = user_messages[original_message_id]
        user_id = user_info['user_id']
        user_name = user_info['user_name']
        
        logger.info(f"📤 Sending reply to user {user_id} ({user_name})")
        
        # Send reply to user
        try:
            bot.send_message(user_id, f"💌 Reply from support:\n\n{reply_text}")
            logger.info(f"✅ Reply sent to user {user_id}")
            
            # Confirm to admin
            bot.reply_to(message, f"✅ Reply sent to {user_name} (ID: {user_id})")
            
        except Exception as e:
            error_msg = f"❌ Failed to send to user: {str(e)}"
            bot.reply_to(message, error_msg)
            logger.error(error_msg)
        
    except ValueError:
        bot.reply_to(message, "❌ Invalid message ID. Must be a number.")
    except Exception as e:
        error_msg = f"❌ Unexpected error: {str(e)}"
        bot.reply_to(message, error_msg)
        logger.error(error_msg)

# Admin help command
@bot.message_handler(commands=['admin', 'help'])
def admin_help(message):
    if str(message.from_user.id) != ADMIN_CHAT_ID:
        return
    
    recent_ids = list(user_messages.keys())[-5:] if user_messages else "No recent messages"
    
    help_text = f"""
🤖 *Admin Commands:*

/reply MESSAGE_ID Your message here
- Reply to any user message

*Example:*
/reply 320 Hello! I can help you with that.

*Recent message IDs:* {recent_ids}

*Bot Status:* ✅ Running
"""
    bot.reply_to(message, help_text)

# Test command to check if bot is working
@bot.message_handler(commands=['test'])
def test_command(message):
    if str(message.from_user.id) != ADMIN_CHAT_ID:
        return
        
    recent_ids = list(user_messages.keys())[-5:] if user_messages else "No recent messages"
    bot.reply_to(message, f"🤖 Bot is working!\nAdmin ID: {ADMIN_CHAT_ID}\nRecent messages: {recent_ids}")
    logger.info("Test command executed")

# Run bot polling with single instance check
def run_bot():
    global bot_running
    
    if bot_running:
        logger.info("⚠️ Bot instance already running, skipping...")
        return
        
    bot_running = True
    logger.info("🚀 Starting Telegram bot polling...")
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found")
        return
    
    if not ADMIN_CHAT_ID:
        logger.error("❌ ADMIN_CHAT_ID not found")
        return
    
    try:
        # Test bot connection
        bot_info = bot.get_me()
        logger.info(f"✅ Bot connected: @{bot_info.username}")
        
        # Send startup message to admin
        bot.send_message(ADMIN_CHAT_ID, f"🤖 Bot started successfully!\nBot: @{bot_info.username}\nUse /admin for commands")
        logger.info("✅ Startup message sent to admin")
        
        # Start polling with error handling
        logger.info("🔄 Starting polling...")
        bot.infinity_polling(timeout=60, long_polling_timeout=60, logger_level=logging.INFO)
        
    except Exception as e:
        logger.error(f"❌ Bot polling error: {e}")
        bot_running = False
        import time
        time.sleep(30)  # Wait longer before restart
        logger.info("🔄 Restarting bot...")
        run_bot()

# Start bot in a thread
def start_bot():
    try:
        bot_thread = Thread(target=run_bot, daemon=True)
        bot_thread.start()
        logger.info("✅ Bot thread started successfully")
    except Exception as e:
        logger.error(f"❌ Failed to start bot thread: {e}")

# Main function
def main():
    logger.info("🎯 Starting application...")
    
    # Validate environment variables
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN environment variable is not set")
        return
    
    if not ADMIN_CHAT_ID:
        logger.error("❌ ADMIN_CHAT_ID environment variable is not set")
        return
    
    logger.info(f"🔑 Bot Token: {BOT_TOKEN[:10]}...")
    logger.info(f"👤 Admin ID: {ADMIN_CHAT_ID}")
    
    # Start the bot (only one instance)
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
