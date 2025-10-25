import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

# Read BOT_TOKEN from environment (set in Railway)
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN not found. Please set it in Railway Environment Variables.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Main Menu Buttons ---
row1 = [KeyboardButton(text="🔐 OTP Mode"), KeyboardButton(text="➕ Plus Add")]
row2 = [KeyboardButton(text="📋 Easy Copy"), KeyboardButton(text="📧 Email Generator")]
row3 = [KeyboardButton(text="👤 Name Generator"), KeyboardButton(text="🌍 Fake Data")]
row4 = [KeyboardButton(text="🧠 AI Mode"), KeyboardButton(text="📦 Bulk Export")]
row5 = [KeyboardButton(text="🏠 Main Menu"), KeyboardButton(text="ℹ️ Help")]

main_kb = ReplyKeyboardMarkup(
    keyboard=[row1, row2, row3, row4, row5],
    resize_keyboard=True,
    input_field_placeholder="Choose a tool…"
)

WELCOME = (
    "👋 Welcome to **DataVers TG!**\n"
    "Your all-in-one data toolkit.\n\n"
    "Choose any tool from the menu below."
)

@dp.message(CommandStart())
async def start_cmd(message: Message):
    await message.answer(WELCOME, reply_markup=main_kb, parse_mode="Markdown")

@dp.message(Command("menu"))
async def menu_cmd(message: Message):
    await message.answer("📎 Main menu:", reply_markup=main_kb)

# --- Placeholder Handlers ---
@dp.message(F.text == "🔐 OTP Mode")
async def otp_mode(message: Message):
    await message.answer("🔐 OTP Mode — coming soon!")

@dp.message(F.text == "➕ Plus Add")
async def plus_add(message: Message):
    await message.answer("➕ Plus Add — phone extract/format/export coming soon!")

@dp.message(F.text == "📋 Easy Copy")
async def easy_copy(message: Message):
    await message.answer("📋 Easy Copy — coming soon!")

@dp.message(F.text == "📧 Email Generator")
async def email_gen(message: Message):
    await message.answer("📧 Email Generator — coming soon!")

@dp.message(F.text == "👤 Name Generator")
async def name_gen(message: Message):
    await message.answer("👤 Name Generator — coming soon!")

@dp.message(F.text == "🌍 Fake Data")
async def fake_data(message: Message):
    await message.answer("🌍 Fake Data — coming soon!")

@dp.message(F.text == "🧠 AI Mode")
async def ai_mode(message: Message):
    await message.answer("🧠 AI Mode — coming soon!")

@dp.message(F.text == "📦 Bulk Export")
async def bulk_export(message: Message):
    await message.answer("📦 Bulk Export — coming soon!")

@dp.message(F.text == "🏠 Main Menu")
async def back_home(message: Message):
    await message.answer("🏠 Back to main menu.", reply_markup=main_kb)

@dp.message(F.text == "ℹ️ Help")
async def help_cmd(message: Message):
    await message.answer(
        "ℹ️ **Help Menu**\n"
        "- Use /start or /menu to view the menu\n"
        "- Each feature will be added step-by-step\n"
        "- Deploy target: Railway"
    )

async def main():
    print("🤖 DataVers TG is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
