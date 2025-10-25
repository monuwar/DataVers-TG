import os
import random
import asyncio
import logging
# 🔧 Auto create name dataset if missing
if not os.path.exists("names"):
    import name_dataset_builder
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

# ------------ MAIN MENU UI (Unchanged) ------------
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🧠 Name Generator"), KeyboardButton(text="📧 Email Generator")],
        [KeyboardButton(text="🔢 OTP Mode"), KeyboardButton(text="🧩 Fake Data")],
        [KeyboardButton(text="➕ Plus Add"), KeyboardButton(text="🏠 Main Menu")]
    ],
    resize_keyboard=True
)

gender_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Male"), KeyboardButton(text="Female")],
        [KeyboardButton(text="Mixed"), KeyboardButton(text="🏠 Main Menu")]
    ],
    resize_keyboard=True
)

# ------------ USER CONTEXT ------------
user_state = {}

def reset_state(uid: int):
    user_state.pop(uid, None)

# ------------ FILE LOADER ------------
def load_names(country: str, gender: str):
    """Load names from one combined file per country-gender (First+Last same file)"""
    base = country.lower()
    g = gender.lower()
    paths = [
        f"names/{base}_{g}.txt",
        f"names/{base}.txt"  # fallback
    ]
    for path in paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return [ln.strip() for ln in f if ln.strip()]
    return []

# ------------ START ------------
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    reset_state(message.from_user.id)
    await message.answer(
        "👋 Welcome to <b>DataVers TG Bot!</b>\n\nChoose an option below 👇",
        reply_markup=main_menu
    )

# ------------ MAIN BUTTONS (placeholders except Name Generator) ------------
@dp.message(F.text.in_(["📧 Email Generator", "🔢 OTP Mode", "🧩 Fake Data", "➕ Plus Add"]))
async def other_features(message: types.Message):
    reset_state(message.from_user.id)
    await message.answer("⚙️ This feature is coming soon... stay tuned!")

@dp.message(F.text == "🏠 Main Menu")
async def main_menu_back(message: types.Message):
    reset_state(message.from_user.id)
    await message.answer("🏠 Main Menu:\nSelect an option 👇", reply_markup=main_menu)

# ------------ NAME GENERATOR FLOW ------------
@dp.message(F.text == "🧠 Name Generator")
async def ask_country(message: types.Message):
    reset_state(message.from_user.id)
    user_state[message.from_user.id] = {"step": "country"}
    await message.answer("🌍 Type a country name (e.g. Bangladesh, India, Japan, USA)")

@dp.message(lambda m: user_state.get(m.from_user.id, {}).get("step") == "country")
async def got_country(message: types.Message):
    country = message.text.strip()
    user_state[message.from_user.id] = {"step": "gender", "country": country}
    await message.answer(
        f"✅ Country selected: {country.title()}\n\nPlease select a gender:",
        reply_markup=gender_menu
    )

@dp.message(lambda m: user_state.get(m.from_user.id, {}).get("step") == "gender")
async def got_gender(message: types.Message):
    g = message.text.strip().lower()
    if g not in ["male", "female", "mixed"]:
        await message.answer("❌ Please select: Male / Female / Mixed", reply_markup=gender_menu)
        return

    user_state[message.from_user.id]["gender"] = g
    user_state[message.from_user.id]["step"] = "count"

    await message.answer(
        f"✅ Gender selected: {g.title()}\n\n📊 How many names do you want?\n💡 Suggested: 10–50\n📈 Maximum: 5000\n\nPlease enter a number:"
    )

@dp.message(lambda m: user_state.get(m.from_user.id, {}).get("step") == "count")
async def got_count(message: types.Message):
    uid = message.from_user.id
    if not message.text.isdigit():
        await message.answer("❌ Please enter a valid number.")
        return

    count = int(message.text)
    if count < 1 or count > 5000:
        await message.answer("❌ Enter between 1 and 5000.")
        return

    country = user_state[uid]["country"]
    gender = user_state[uid]["gender"]

    # load names
    names = load_names(country, gender)
    if not names:
        reset_state(uid)
        await message.answer(
            f"❌ No name data found for {country.title()} ({gender}).\n"
            f"📁 Expected file: <code>names/{country.lower()}_{gender}.txt</code> or <code>names/{country.lower()}.txt</code>",
            reply_markup=main_menu
        )
        return

    # generate random names
    generated = random.sample(names, k=min(count, len(names)))

    if count <= 200:
        text = "\n".join(generated)
        await message.answer(
            f"🎉 SUCCESS!\n✅ Generated {count} {gender.title()} names from {country.title()}:\n\n<code>{text}</code>"
        )
    else:
        filename = f"{country.lower()}_{gender}_names.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(generated))
        await message.answer_document(
            open(filename, "rb"),
            caption=f"✅ Generated {count} {gender.title()} names from {country.title()} saved as file."
        )
        os.remove(filename)

    reset_state(uid)

# ------------ RUN ------------
async def main():
    print("🚀 DataVers TG Bot is running...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
