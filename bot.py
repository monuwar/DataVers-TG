import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.enums import ParseMode

# ========== BOT SETUP ==========
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN is missing in environment variables!")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# ========== IMPORT HANDLERS ==========
from handlers import name_generator
dp.include_router(name_generator.router)

# ========== MAIN MENU ==========
def main_menu():
    buttons = [
        [KeyboardButton(text="🧠 Name Generator"), KeyboardButton(text="📧 Email Generator")],
        [KeyboardButton(text="🔢 OTP Mode"), KeyboardButton(text="🧩 Fake Data")],
        [KeyboardButton(text="➕ Plus Add"), KeyboardButton(text="🏠 Main Menu")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# ========== /start ==========
@dp.message(F.text == "/start")
async def start_command(message: Message):
    txt = (
        "👋 <b>Welcome to DataVers TG!</b>\n\n"
        "✨ Generate data, names, and more right from Telegram!\n\n"
        "Choose a tool below 👇"
    )
    await message.answer(txt, reply_markup=main_menu())

# ========== NAME GENERATOR BUTTON ==========
@dp.message(F.text.regexp(r"(?i)(name\s*generator)"))
async def open_name_generator(message: Message):
    await name_generator.ng_start(message)

# ========== EMAIL GENERATOR ==========
@dp.message(F.text == "📧 Email Generator")
async def email_gen(message: Message):
    await message.answer("📨 Email Generator — coming soon!")

# ========== OTP MODE ==========
@dp.message(F.text == "🔢 OTP Mode")
async def otp_mode(message: Message):
    await message.answer("🔒 OTP Mode — coming soon!")

# ========== FAKE DATA ==========
@dp.message(F.text == "🧩 Fake Data")
async def fake_data(message: Message):
    await message.answer("🧩 Fake Data — coming soon!")

# ========== PLUS ADD ==========
@dp.message(F.text == "➕ Plus Add")
async def plus_add(message: Message):
    await message.answer("➕ Plus Add — phone extract/format/export coming soon!")

# ========== MAIN MENU ==========
@dp.message(F.text == "🏠 Main Menu")
async def back_main(message: Message):
    await message.answer("🏠 Back to main menu!", reply_markup=main_menu())

# ========== FALLBACK ==========
@dp.message()
async def fallback(message: Message):
    await message.answer("❓ Please choose an option from the menu.", reply_markup=main_menu())

# ========== RUN BOT ==========
async def main():
    print("🚀 DataVers TG Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
