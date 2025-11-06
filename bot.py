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

# Store user data for replies (in production, use a database)
user_messages = {}

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
    user_info = f"🆕 New user started the bot:\nID: `{user.id}`\nName: {user.first_name}\nUsername: @{user.username}"
    
    try:
        bot.send_message(ADMIN_CHAT_ID, user_info, parse_mode='Markdown')
        logger.info(f"New user: {user.id} - {user.first_name}")
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")

# Handle all user messages and forward to admin
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'document'])
def handle_all_messages(message):
    user = message.from_user
    
    # Create a unique ID for this message
    message_id = message.message_id
    
    # Store user info with message ID
    user_messages[message_id] = {
        'user_id': user.id,
        'user_name': user.first_name,
        'username': user.username
    }
    
    # Forward message to admin based on content type
    if message.text:
        forward_text_message(message, message_id)
    elif message.photo:
        forward_photo_message(message, message_id)
    elif message.document:
        forward_document_message(message, message_id)

def forward_text_message(message, message_id):
    user = message.from_user
    user_info = f"💬 Message #`{message_id}`\nFrom: {user.first_name} (@{user.username})\nUser ID: `{user.id}`"
    
    try:
        # Send message to admin with reply instructions
        admin_message = f"{user_info}\n\n📩 {message.text}\n\n💡 *Reply to this user by typing:*\n`/reply {message_id} Your message here`"
        bot.send_message(ADMIN_CHAT_ID, admin_message, parse_mode='Markdown')
        
        # Auto-reply to user
        bot.reply_to(message, "✅ Message received! I will reply to you when I come online. Please be patient...")
        
        logger.info(f"Forwarded text message #{message_id} from user {user.id}")
        
    except Exception as e:
        logger.error(f"Error forwarding message: {e}")
        bot.reply_to(message, "❌ Failed to send message. Please try again later.")

def forward_photo_message(message, message_id):
    user = message.from_user
    user_info = f"🖼️ Photo #`{message_id}`\nFrom: {user.first_name} (@{user.username})\nUser ID: `{user.id}`"
    
    try:
        # Send to admin with reply instructions
        caption = message.caption if message.caption else "No caption"
        admin_message = f"{user_info}\n\n📸 {caption}\n\n💡 *Reply to this user by typing:*\n`/reply {message_id} Your message here`"
        
        bot.send_message(ADMIN_CHAT_ID, admin_message, parse_mode='Markdown')
        bot.send_photo(ADMIN_CHAT_ID, message.photo[-1].file_id)
        
        # Auto-reply to user
        bot.reply_to(message, "✅ Photo received! I will check it and reply when I come online.")
        
        logger.info(f"Forwarded photo #{message_id} from user {user.id}")
        
    except Exception as e:
        logger.error(f"Error forwarding photo: {e}")
        bot.reply_to(message, "❌ Failed to send photo. Please try again later.")

def forward_document_message(message, message_id):
    user = message.from_user
    user_info = f"📎 Document #`{message_id}`\nFrom: {user.first_name} (@{user.username})\nUser ID: `{user.id}`"
    
    try:
        # Send to admin with reply instructions
        caption = message.caption if message.caption else "No caption"
        admin_message = f"{user_info}\n\n📄 {caption}\n\n💡 *Reply to this user by typing:*\n`/reply {message_id} Your message here`"
        
        bot.send_message(ADMIN_CHAT_ID, admin_message, parse_mode='Markdown')
        bot.send_document(ADMIN_CHAT_ID, message.document.file_id)
        
        # Auto-reply to user
        bot.reply_to(message, "✅ Document received! I will check it and reply when I come online.")
        
        logger.info(f"Forwarded document #{message_id} from user {user.id}")
        
    except Exception as e:
        logger.error(f"Error forwarding document: {e}")
        bot.reply_to(message, "❌ Failed to send document. Please try again later.")

# Admin reply command
@bot.message_handler(commands=['reply'])
def admin_reply(message):
    # Check if user is admin
    if str(message.from_user.id) != ADMIN_CHAT_ID:
        bot.reply_to(message, "❌ Access denied.")
        return
    
    try:
        # Parse command: /reply MESSAGE_ID Your reply text
        parts = message.text.split(' ', 2)
        if len(parts) < 3:
            bot.reply_to(message, "❌ Usage: `/reply MESSAGE_ID Your message here`", parse_mode='Markdown')
            return
        
        original_message_id = int(parts[1])
        reply_text = parts[2]
        
        # Get user info from stored messages
        if original_message_id not in user_messages:
            bot.reply_to(message, "❌ Message ID not found. It might be too old.")
            return
        
        user_info = user_messages[original_message_id]
        user_id = user_info['user_id']
        user_name = user_info['user_name']
        
        # Send reply to user
        bot.send_message(user_id, f"💌 Reply from admin:\n\n{reply_text}")
        
        # Confirm to admin
        bot.reply_to(message, f"✅ Reply sent to {user_name} (ID: {user_id})")
        
        logger.info(f"Admin replied to user {user_id}")
        
    except ValueError:
        bot.reply_to(message, "❌ Invalid message ID. Must be a number.")
    except Exception as e:
        bot.reply_to(message, f"❌ Error sending reply: {str(e)}")
        logger.error(f"Admin reply error: {e}")

# Admin help command
@bot.message_handler(commands=['admin'])
def admin_help(message):
    if str(message.from_user.id) != ADMIN_CHAT_ID:
        bot.reply_to(message, "❌ Access denied.")
        return
    
    help_text = """
🤖 *Admin Commands:*

📩 */reply MESSAGE_ID Your message* 
- Reply to a user's message
- Example: `/reply 123 Hello, I received your message`

👥 */users*
- Show recent users (to be implemented)

📊 */stats*
- Show bot statistics (to be implemented)

💡 *How to reply:*
1. When a user messages, you'll get a message with a number like `Message #123`
2. Use `/reply 123 Your message` to reply to that user
3. The user will receive your message directly
"""
    bot.reply_to(message, help_text, parse_mode='Markdown')

# Run bot polling
def run_bot():
    logger.info("🚀 Starting Telegram bot...")
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found")
        return
    
    if not ADMIN_CHAT_ID:
        logger.error("❌ ADMIN_CHAT_ID not found")
        return
    
    try:
        logger.info("✅ Bot configured successfully")
        logger.info("🔄 Starting polling...")
        
        # Send startup message to admin
        bot.send_message(ADMIN_CHAT_ID, "🤖 Bot started successfully!\nUse /admin for commands.")
        
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
        
    except Exception as e:
        logger.error(f"❌ Bot polling error: {e}")
        import time
        time.sleep(10)
        run_bot()  # Restart

# Start bot in a thread
def start_bot():
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("✅ Bot thread started")

# Main function
def main():
    if not BOT_TOKEN or not ADMIN_CHAT_ID:
        logger.error("❌ Missing environment variables")
        return
    
    logger.info("🎯 Starting application...")
    start_bot()
    
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🌐 Starting Flask app on port {port}")
    
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    main()
