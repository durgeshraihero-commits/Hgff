import logging
import os
os.environ["PORT"] = "8080"
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.dispatcher.filters import CommandStart
from aiogram.utils import executor
from dotenv import load_dotenv

# --------------------------
# Load environment variables
# --------------------------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# --------------------------
# Setup logging and bot
# --------------------------
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# --------------------------
# Handle /start command
# --------------------------
@dp.message_handler(CommandStart())
async def start(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Share Phone Number", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(
        "👋 Welcome to the Support Bot!\n"
        "Please describe your issue or share your phone number below 👇",
        reply_markup=keyboard
    )

# --------------------------
# Handle contact (phone number)
# --------------------------
@dp.message_handler(content_types=types.ContentType.CONTACT)
async def handle_contact(message: Message):
    contact = message.contact
    phone_number = contact.phone_number
    user_id = message.chat.id

    # Notify admin
    await bot.send_message(
        ADMIN_ID,
        f"📞 User shared phone number:\n\n"
        f"👤 Name: {message.from_user.full_name}\n"
        f"📱 Phone: {phone_number}\n"
        f"🆔 ID: `{user_id}`",
        parse_mode="Markdown"
    )

    await message.answer("✅ Thanks! Your phone number has been shared with support.")

# --------------------------
# Forward user messages to admin
# --------------------------
@dp.message_handler(lambda message: message.chat.id != ADMIN_ID)
async def forward_to_admin(message: Message):
    user = message.from_user
    username = f"@{user.username}" if user.username else "❌ No username"
    name = user.full_name or "Unknown"
    user_id = user.id

    # Forward message
    await bot.forward_message(ADMIN_ID, user_id, message.message_id)

    # Send info about sender
    info_text = (
        f"🧾 Message from user:\n\n"
        f"👤 Name: {name}\n"
        f"🆔 ID: `{user_id}`\n"
        f"🔗 Username: {username}"
    )
    await bot.send_message(ADMIN_ID, info_text, parse_mode="Markdown")

# --------------------------
# Admin reply to user
# --------------------------
@dp.message_handler(lambda message: message.chat.id == ADMIN_ID and message.reply_to_message)
async def reply_from_admin(message: Message):
    text = message.reply_to_message.text or ""
    if "ID:" in text:
        try:
            user_id = int(text.split("ID:")[1].split("\n")[0].strip(' `'))
            await bot.send_message(user_id, f"💬 Support Reply:\n\n{message.text}")
            await message.answer("✅ Sent to user.")
        except Exception as e:
            await message.answer(f"⚠️ Failed to send: {e}")
    else:
        await message.answer("⚠️ Can't find user ID to reply.")

# --------------------------
# Run the bot
# --------------------------
if __name__ == "__main__":
    logging.info("🚀 Bot started successfully!")
    executor.start_polling(dp, skip_updates=True)
