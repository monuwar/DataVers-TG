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
    raise RuntimeError("BOT_TOKEN environment variable missing!")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ------------ REPLY KEYBOARD (Main Menu) ------------
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🧠 Name Generator"), KeyboardButton(text="📧 Email Generator")],
        [KeyboardButton(text="🔢 OTP Mode"), KeyboardButton(text="🧩 Fake Data")],
        [KeyboardButton(text="➕ Plus Add"), KeyboardButton(text="🏠 Main Menu")]
    ],
    resize_keyboard=True
)

# ------------ MEMORY (to store user steps) ------------
user_context = {}

# ------------ HELPERS ------------
def load_names(country: str, gender: str):
    """Load names from text file"""
    path = f"names/{country.lower()}_{gender.lower()}.txt"
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def combine_names(first_list, last_list, count):
    """Create random first+last combinations"""
    result = []
    for _ in range(count):
        first = random.choice(first_list)
        last = random.choice(last_list)
        result.append(f"{first} {last}")
    return result

# ------------ COMMAND / START ------------
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "👋 Welcome to <b>DataVers TG Bot!</b>\n\nChoose an option below 👇",
        reply_markup=main_menu
    )

# ------------ NAME GENERATOR ENTRY ------------
@dp.message(F.text == "🧠 Name Generator")
async def ask_country(message: types.Message):
    await message.answer("🌍 Type a country name (e.g. Bangladesh, India, Japan, USA)")
    user_context[message.from_user.id] = {"step": "country"}

# ------------ HANDLE COUNTRY NAME ------------
@dp.message(lambda msg: user_context.get(msg.from_user.id, {}).get("step") == "country")
async def handle_country(message: types.Message):
    country = message.text.strip().lower()
    user_context[message.from_user.id] = {"country": country, "step": "gender"}

    await message.answer(
        f"✅ Country selected: {country.title()}\n\nPlease select a gender:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Male"), KeyboardButton(text="Female")],
                [KeyboardButton(text="Mixed"), KeyboardButton(text="🏠 Main Menu")]
            ],
            resize_keyboard=True
        )
    )

# ------------ HANDLE GENDER ------------
@dp.message(lambda msg: user_context.get(msg.from_user.id, {}).get("step") == "gender")
async def handle_gender(message: types.Message):
    gender = message.text.strip().lower()
    if gender not in ["male", "female", "mixed"]:
        await message.answer("❌ Invalid input. Please choose: Male / Female / Mixed")
        return

    user_context[message.from_user.id]["gender"] = gender
    user_context[message.from_user.id]["step"] = "count"

    await message.answer(
        f"✅ Gender selected: {gender.title()}\n\n📊 How many names do you want?\n"
        "💡 Suggested: 10–50\n📈 Maximum: 5000\n\nPlease enter a number:"
    )

# ------------ HANDLE COUNT & GENERATE ------------
@dp.message(lambda msg: user_context.get(msg.from_user.id, {}).get("step") == "count")
async def handle_count(message: types.Message):
    uid = message.from_user.id
    if not message.text.isdigit():
        await message.answer("❌ Please enter a valid number.")
        return

    count = int(message.text)
    if count < 1 or count > 5000:
        await message.answer("❌ Enter between 1 and 5000.")
        return

    country = user_context[uid]["country"]
    gender = user_context[uid]["gender"]

    # Determine which files to load
    if gender == "mixed":
        male_names = load_names(country, "male")
        female_names = load_names(country, "female")
        all_first = male_names + female_names
        all_last = male_names + female_names
    elif gender == "male":
        all_first = load_names(country, "male")
        all_last = load_names(country, "male")
    else:
        all_first = load_names(country, "female")
        all_last = load_names(country, "female")

    if not all_first or not all_last:
        await message.answer(f"❌ No name data found for {country.title()} ({gender}).")
        return

    generated = combine_names(all_first, all_last, count)

    if count <= 200:
        await message.answer(
            f"🎉 SUCCESS!\n✅ Generated {count} {gender.title()} names from {country.title()}:\n\n<code>"
            + "\n".join(generated)
            + "</code>"
        )
    else:
        filename = f"{country}_{gender}_names.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(generated))
        await message.answer_document(
            open(filename, "rb"),
            caption=f"✅ Generated {count} {gender.title()} names from {country.title()} saved as file."
        )
        os.remove(filename)

    user_context.pop(uid, None)  # clear user context

# ------------ OTHER BUTTONS ------------
@dp.message(F.text.in_(["📧 Email Generator", "🔢 OTP Mode", "🧩 Fake Data", "➕ Plus Add"]))
async def coming_soon(message: types.Message):
    await message.answer("⚙️ This feature is coming soon... stay tuned!")

@dp.message(F.text == "🏠 Main Menu")
async def go_home(message: types.Message):
    await message.answer("🏠 Main Menu:\nSelect an option 👇", reply_markup=main_menu)
    user_context.pop(message.from_user.id, None)

# ------------ RUN ------------
async def main():
    print("🚀 DataVers TG Bot is running...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
