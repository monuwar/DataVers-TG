import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.enums import ParseMode
import os

# ======== Load Token from Railway Environment ========
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ======== Bot Initialization ========
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# ======== Import All Handlers ========
from handlers import name_generator
dp.include_router(name_generator.router)

# ======== Main Menu Keyboard ========
def main_menu():
    buttons = [
        [KeyboardButton(text="🧠 Name Generator")],
        [KeyboardButton(text="📧 Email Generator")],
        [KeyboardButton(text="🔢 OTP Mode")],
        [KeyboardButton(text="🧩 Fake Data")],
        [KeyboardButton(text="🏠 Main Menu")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# ======== Start Command ========
@dp.message(F.text == "/start")
async def start_command(message: Message):
    text = (
        "👋 <b>Welcome to DataVers TG Bot!</b>\n\n"
        "Choose a tool below to get started 👇"
    )
    await message.answer(text, reply_markup=main_menu())

# ======== Main Menu Button ========
@dp.message(F.text == "🏠 Main Menu")
async def go_main_menu(message: Message):
    await message.answer("🏠 Back to main menu!", reply_markup=main_menu())

# ======== Fallback Message (unknown text) ========
@dp.message()
async def fallback(message: Message):
    await message.answer("❓ Please choose an option from the menu.", reply_markup=main_menu())

# ======== Run Bot ========
async def main():
    print("🤖 DataVers TG Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
