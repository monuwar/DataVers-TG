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
fake_sessions = {}  # { user_id: {"step": "country" | "gender", "country": ""} }
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
    
@dp.message(lambda m: m.text == "🧩 Fake Data")
async def fake_data_start(message: types.Message):
    uid = message.from_user.id
    fake_sessions[uid] = {"step": "country", "country": ""}
    await message.answer("🌍 Please type a country name (e.g. Bangladesh, Japan, USA)")

@dp.message(lambda m: m.from_user.id in fake_sessions and fake_sessions[m.from_user.id]["step"] == "country")
async def fake_data_country(message: types.Message):
    uid = message.from_user.id
    country = message.text.strip()
    fake_sessions[uid]["country"] = country
    fake_sessions[uid]["step"] = "gender"

    await message.answer(
        f"✅ Country selected: {country.title()}\n\nPlease select a gender:",
        reply_markup=gender_menu
    )

@dp.message(lambda m: m.from_user.id in fake_sessions and fake_sessions[m.from_user.id]["step"] == "gender")
async def fake_data_gender(message: types.Message):
    uid = message.from_user.id
    gender = message.text.strip().lower()

    if gender not in ["male", "female", "mixed"]:
        await message.answer("❌ Please select: Male / Female / Mixed", reply_markup=gender_menu)
        return

    fake_sessions[uid]["gender"] = gender
    fake_sessions[uid]["step"] = "count"

    await message.answer(
        f"✅ Gender selected: {gender.title()}\n\n📊 How many fake data entries do you want?\n💡 Suggested: 10–50\n📈 Maximum: 5000"
    )

@dp.message(lambda m: m.from_user.id in fake_sessions and fake_sessions[m.from_user.id]["step"] == "count")
async def fake_data_count(message: types.Message):
    uid = message.from_user.id
    txt = message.text.strip()

    # সংখ্যা কিনা চেক
    if not txt.isdigit():
        await message.answer("❌ Please enter a valid number (digits only).")
        return

    n = int(txt)
    if n < 1 or n > 5000:
        await message.answer("❌ Enter between 1 and 5000.")
        return

    # সেভ করে পরের স্টেপে যাই
    fake_sessions[uid]["count"] = n
    fake_sessions[uid]["step"] = "fields"

    # ইউজারকে কোন কোন ফিল্ড চাই জিজ্ঞেস করি
    await message.answer(
        "🧩 What fields do you want?\n"
        "👉 Send a comma-separated list, e.g.\n"
        "<code>first_name,last_name,age,city,phone,email</code>\n\n"
        "📋 Available fields:\n"
        "first_name, last_name, full_name, username, age, gender, "
        "city, state, country, postal_code, address, phone, email, "
        "job, company, uuid",
        parse_mode="HTML"
    )

from faker import Faker

@dp.message(lambda m: m.from_user.id in fake_sessions and fake_sessions[m.from_user.id]["step"] == "fields")
async def fake_data_fields(message: types.Message):
    uid = message.from_user.id
    fields = [f.strip().lower() for f in message.text.split(",") if f.strip()]
    if not fields:
        await message.answer("❌ Please enter at least one valid field.")
        return

    fake_sessions[uid]["fields"] = fields
    fake_sessions[uid]["step"] = "done"

    country = fake_sessions[uid]["country"]
    gender = fake_sessions[uid]["gender"]
    count = fake_sessions[uid]["count"]

    faker = Faker()
    data = []

    for _ in range(count):
        entry = {}
        for f in fields:
            try:
                if f == "first_name":
                    entry[f] = faker.first_name_male() if gender == "male" else faker.first_name_female()
                elif f == "last_name":
                    entry[f] = faker.last_name()
                elif f == "full_name":
                    fn = faker.first_name_male() if gender == "male" else faker.first_name_female()
                    entry[f] = f"{fn} {faker.last_name()}"
                elif hasattr(faker, f):
                    entry[f] = str(getattr(faker, f)())
                else:
                    entry[f] = "N/A"
            except Exception:
                entry[f] = "N/A"
        data.append(entry)

    # ফলাফল মেসেজ বানানো
    preview = "\n".join([", ".join(f"{k}: {v}" for k, v in d.items()) for d in data[:10]])
    await message.answer(f"🎉 SUCCESS!\n✅ Generated {count} fake data entries for {country.title()}:\n\n{preview}")

# বড় লিস্ট হলে টেক্সট ফাইল হিসেবে পাঠানো
    if count > 200:
        import io
        output = io.StringIO()
        for d in data:
            line = ", ".join(f"{k}: {v}" for k, v in d.items())
            output.write(line + "\n")
        output.seek(0)
        await message.answer_document(
            types.InputFile(output, filename=f"{country.lower()}_fake_data.txt"),
            caption=f"📄 Generated {count} fake data entries for {country.title()}!"
        )
        fake_sessions.pop(uid, None)
        return
    
    fake_sessions.pop(uid, None)

import random

@dp.message(F.text == "📅 OTP Mode")
async def otp_mode_start(message: types.Message):
    await message.answer(
        "🔢 Welcome to OTP Mode!\n"
        "Please choose an OTP type:\n"
        "1️⃣ SMS OTP (4–6 digits)\n"
        "2️⃣ Email OTP (code with letters)\n"
        "3️⃣ Custom Length OTP",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="SMS OTP"), KeyboardButton(text="Email OTP")],
                [KeyboardButton(text="Custom OTP"), KeyboardButton(text="🏠 Main Menu")]
            ],
            resize_keyboard=True
        )
    )

import asyncio
from datetime import datetime, timedelta

otp_sessions = {}

@dp.message(lambda m: m.text in ["SMS OTP", "Email OTP", "Custom OTP"])
async def otp_generate(message: types.Message):
    uid = message.from_user.id
    otp_type = message.text
    otp = ""

    if otp_type == "SMS OTP":
        otp = str(random.randint(1000, 999999))
    elif otp_type == "Email OTP":
        otp = ''.join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=8))
    elif otp_type == "Custom OTP":
        await message.answer("✏️ Enter custom OTP length (e.g. 4–10):")
        otp_sessions[uid] = {"step": "custom_length"}
        return

    expire = datetime.utcnow() + timedelta(minutes=1)
    otp_sessions[uid] = {"otp": otp, "expire": expire}

    await message.answer(
        f"✅ Your {otp_type} is: <b>{otp}</b>\n"
        f"⚠️ This OTP will expire in 1 minute!",
        parse_mode="HTML"
    )

    await asyncio.sleep(60)
    if uid in otp_sessions and datetime.utcnow() > otp_sessions[uid]["expire"]:
        otp_sessions.pop(uid, None)
        await message.answer("⌛ Your OTP has expired!")

@dp.message(lambda m: m.from_user.id in otp_sessions and otp_sessions[m.from_user.id].get("step") == "custom_length")
async def otp_custom_length(message: types.Message):
    uid = message.from_user.id
    if not message.text.isdigit():
        await message.answer("❌ Please enter a valid number!")
        return

    length = int(message.text)
    if length < 3 or length > 12:
        await message.answer("⚠️ Length should be between 3–12!")
        return

    otp = ''.join(random.choices("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=length))
    expire = datetime.utcnow() + timedelta(minutes=1)
    otp_sessions[uid] = {"otp": otp, "expire": expire}

    await message.answer(
        f"✅ Custom OTP ({length} digits): <b>{otp}</b>\n"
        f"⌛ This OTP will expire in 1 minute!",
        parse_mode="HTML"
    )

    await asyncio.sleep(60)
    if uid in otp_sessions and datetime.utcnow() > otp_sessions[uid]["expire"]:
        otp_sessions.pop(uid, None)
        await message.answer("⌛ Your OTP has expired!")

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
