import os
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.utils import executor

# -------------------- BOT SETUP --------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(bot)

# -------------------- UI BUTTONS --------------------
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🧠 Name Generator", callback_data="namegen")],
    [InlineKeyboardButton(text="📊 Data Tools", callback_data="tools")],
    [InlineKeyboardButton(text="📢 About Bot", callback_data="about")]
])

back_btn = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="back")]
])

# -------------------- COMMANDS --------------------
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer(
        "👋 Welcome to <b>DataVers TG Bot</b>!\n\nChoose an option below 👇",
        reply_markup=main_menu
    )

# -------------------- CALLBACKS --------------------
@dp.callback_query_handler(lambda c: c.data == "back")
async def go_back(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(
        "🏠 Main Menu:\nSelect a feature 👇",
        reply_markup=main_menu
    )

@dp.callback_query_handler(lambda c: c.data == "about")
async def about(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(
        "🤖 <b>DataVers TG Bot</b>\n\nDeveloped by Team DataVers.\n\n⚙️ Features:\n• Name Generator\n• Data Tools\n\nVersion: 1.0.0",
        reply_markup=back_btn
    )

# -------------------- NAME GENERATOR --------------------
@dp.callback_query_handler(lambda c: c.data == "namegen")
async def name_generator(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(
        "🧠 <b>Name Generator</b>\n\nSend me how many names you want (e.g. 50 or 500).",
        reply_markup=back_btn
    )

@dp.message_handler(lambda message: message.text.isdigit())
async def generate_names(message: types.Message):
    count = int(message.text)
    names = [f"Name_{random.randint(1000,9999)}" for _ in range(count)]

    if count <= 200:
        text = "\n".join(names)
        await message.answer(f"✅ Generated {count} names:\n\n<code>{text}</code>")
    else:
        filename = "generated_names.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(names))
        await message.answer_document(open(filename, "rb"), caption=f"✅ Generated {count} names saved as file.")
        os.remove(filename)

# -------------------- DATA TOOLS (PLACEHOLDER) --------------------
@dp.callback_query_handler(lambda c: c.data == "tools")
async def tools(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(
        "📊 <b>Data Tools Section</b>\n\nComing soon...",
        reply_markup=back_btn
    )

# -------------------- MAIN --------------------
if __name__ == "__main__":
    print("🚀 DataVers TG Bot is running...")
    executor.start_polling(dp, skip_updates=True)
