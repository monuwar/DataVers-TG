import os
import random
import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

# ------------ Logging ------------
logging.basicConfig(level=logging.INFO)

# ------------ BOT SETUP ------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN env var missing!")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ------------ MAIN MENU ------------
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🧠 Name Generator"), KeyboardButton(text="📧 Email Generator")],
        [KeyboardButton(text="🔢 OTP Mode"), KeyboardButton(text="🧩 Fake Data")],
        [KeyboardButton(text="➕ Plus Add"), KeyboardButton(text="🏠 Main Menu")]
    ],
    resize_keyboard=True
)

# ------------ START COMMAND ------------
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "👋 Welcome to <b>DataVers TG Bot</b>!\n\nChoose an option below 👇",
        reply_markup=main_menu
    )

# ------------ NAME GENERATOR ------------
@dp.message(F.text == "🧠 Name Generator")
async def name_generator(message: types.Message):
    await message.answer(
        "🧠 <b>Name Generator</b>\n\nSend me how many names you want (e.g. 50 or 500)."
    )

@dp.message(F.text.regexp(r'^\d+$'))
async def generate_names(message: types.Message):
    count = int(message.text)
    names = [f"Name_{random.randint(1000,9999)}" for _ in range(count)]

    if count <= 200:
        await message.answer(f"✅ Generated {count} names:\n\n<code>{'\n'.join(names)}</code>")
    else:
        filename = "generated_names.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(names))
        await message.answer_document(open(filename, "rb"),
                                      caption=f"✅ Generated {count} names saved as file.")

# ------------ OTHER BUTTONS (COMING SOON) ------------
@dp.message(F.text.in_(["📧 Email Generator", "🔢 OTP Mode", "🧩 Fake Data", "➕ Plus Add"]))
async def coming_soon(message: types.Message):
    await message.answer("⚙️ This feature is coming soon... stay tuned!")

@dp.message(F.text == "🏠 Main Menu")
async def go_home(message: types.Message):
    await message.answer("🏠 Main Menu:\nSelect an option 👇", reply_markup=main_menu)

# ------------ RUN ------------
async def main():
    print("🚀 DataVers TG Bot is running...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
