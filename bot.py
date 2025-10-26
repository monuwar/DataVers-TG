
import os
import random
import asyncio
import logging
from faker import Faker
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

# Auto create dataset if missing
if not os.path.exists("names"):
    import name_dataset_builder

# Logging
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable missing!")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Menus
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🧠 Name Generator"), KeyboardButton(text="📧 Email Generator")],
        [KeyboardButton(text="📅 OTP Mode"), KeyboardButton(text="🧩 Fake Data")],
        [KeyboardButton(text="➕ Plus Add"), KeyboardButton(text="🏠 Main Menu")]
    ], resize_keyboard=True
)

gender_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Male"), KeyboardButton(text="Female")],
        [KeyboardButton(text="Mixed"), KeyboardButton(text="🏠 Main Menu")]
    ], resize_keyboard=True
)

user_state = {}
fake_sessions = {}

def reset_state(uid: int):
    user_state.pop(uid, None)
    fake_sessions.pop(uid, None)

# File Loader for name generator
def load_names(country: str, gender: str):
    base = country.lower().replace(" ", "_")
    g = gender.lower()
    paths = [f"names/{base}_{g}.txt", f"names/{base}.txt"]
    for path in paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return [ln.strip() for ln in f if ln.strip()]
    return []

# ---------------- START ----------------
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    reset_state(message.from_user.id)
    await message.answer("👋 <b>Welcome to DataVers TG Bot!</b>\n\nChoose an option below 👇", reply_markup=main_menu)

# ---------------- MAIN BUTTONS ----------------
@dp.message(F.text.in_(["📧 Email Generator", "📅 OTP Mode", "➕ Plus Add"]))
async def other_features(message: types.Message):
    reset_state(message.from_user.id)
    await message.answer("⚙️ This feature is coming soon... stay tuned!")

# ---------------- FAKE DATA GENERATOR ----------------
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
    await message.answer(f"✅ Country selected: {country.title()}\nPlease select a gender:", reply_markup=gender_menu)

@dp.message(lambda m: m.from_user.id in fake_sessions and fake_sessions[m.from_user.id]["step"] == "gender")
async def fake_data_gender(message: types.Message):
    uid = message.from_user.id
    gender = message.text.strip().lower()
    if gender not in ["male", "female", "mixed"]:
        await message.answer("❌ Please select: Male / Female / Mixed", reply_markup=gender_menu)
        return
    fake_sessions[uid]["gender"] = gender
    fake_sessions[uid]["step"] = "count"
    await message.answer(f"✅ Gender selected: {gender.title()}\nHow many fake data entries do you want?\n💡 Suggested: 10–50\n📈 Maximum: 5000\n\nPlease enter a number:")
@dp.message(lambda m: m.from_user.id in fake_sessions and fake_sessions[m.from_user.id]["step"] == "count")
async def fake_data_count(message: types.Message):
    uid = message.from_user.id
    txt = message.text.strip()
    if not txt.isdigit():
        await message.answer("❌ Please enter a valid number (digits only).")
        return
    n = int(txt)
    if n < 1 or n > 5000:
        await message.answer("❌ Enter between 1 and 5000.")
        return
    fake_sessions[uid]["count"] = n

    # Generate data
    country = fake_sessions[uid]["country"]
    gender = fake_sessions[uid]["gender"]
    faker = Faker()
    data = []
    for _ in range(n):
        if gender == "male":
            full_name = f"{faker.first_name_male()} {faker.last_name()}"
        elif gender == "female":
            full_name = f"{faker.first_name_female()} {faker.last_name()}"
        else:
            full_name = f"{faker.first_name()} {faker.last_name()}"
        entry = {
            "full_name": full_name,
            "age": random.randint(18, 65),
            "city": faker.city(),
            "email": faker.email(),
            "phone": faker.phone_number(),
            "country": country.title()
        }
        data.append(entry)

    # Output
    if n <= 200:
        preview = "\n".join([f"{d['full_name']} — {d['email']} — {d['city']} ({d['country']})" for d in data])
        await message.answer(f"🎉 SUCCESS!\n✅ Generated {count} fake data entries for {country.title()}:\n\n{preview}")
    else:
        import io
        output = io.StringIO()
        for d in data:
            line = ", ".join([f"{k}: {v}" for k, v in d.items()])
            output.write(line + "\n")
        output.seek(0)
        await message.answer_document(types.InputFile(output, filename=f"{country.lower()}_fake_data.txt"), caption=f"📄 Generated {n} fake data entries for {country.title()}!")
    fake_sessions.pop(uid, None)

# ---------------- NAME GENERATOR ----------------
@dp.message(F.text == "🧠 Name Generator")
async def ask_country(message: types.Message):
    reset_state(message.from_user.id)
    user_state[message.from_user.id] = {"step": "country"}
    await message.answer("🌍 Type a country name (e.g. Bangladesh, India, Japan, USA)")

@dp.message(lambda m: user_state.get(m.from_user.id, {}).get("step") == "country")
async def get_country(message: types.Message):
    uid = message.from_user.id
    country = message.text.strip()
    user_state[uid]["country"] = country
    user_state[uid]["step"] = "gender"
    await message.answer(f"✅ Country selected: {country.title()}\nPlease select a gender:")
@dp.message(lambda m: user_state.get(m.from_user.id, {}).get("step") == "gender")
async def get_gender(message: types.Message):
    uid = message.from_user.id
    g = message.text.strip().lower()
    if g not in ["male", "female", "mixed"]:
        await message.answer("❌ Please select: Male / Female / Mixed", reply_markup=gender_menu)
        return
    user_state[uid]["gender"] = g
    user_state[uid]["step"] = "count"
    await message.answer(f"✅ Gender selected: {g.title()}

📊 How many names do you want?
💡 Suggested: 10–50
📈 Maximum: 5000

Please enter a number:")

@dp.message(lambda m: user_state.get(m.from_user.id, {}).get("step") == "count")
async def get_count(message: types.Message):
    uid = message.from_user.id
    txt = message.text.strip()
    if not txt.isdigit():
        await message.answer("❌ Please enter a valid number.")
        return
    count = int(txt)
    if count < 1 or count > 5000:
        await message.answer("❌ Enter between 1 and 5000.")
        return

    country = user_state[uid]["country"]
    gender = user_state[uid]["gender"]
    names = load_names(country, gender)

    if not names:
        await message.answer(f"❌ No name data found for {country.title()} ({gender}).\n📄 Expected file: names/{country.lower()}_{gender}.txt")
        reset_state(uid)
        return

    random.shuffle(names)
    selected = names[:count]

    if count <= 200:
        await message.answer(f"🎉 SUCCESS!
✅ Generated {count} {gender.title()} names from {country.title()}:

" + "\n".join(selected))
    else:
        import io
        output = io.StringIO("\n".join(selected))
        await message.answer_document(types.InputFile(output, filename=f"{country.lower()}_{gender}_names.txt"), caption=f"📄 Generated {count} {gender.title()} names from {country.title()}!")
    reset_state(uid)

# ---------------- RUN ----------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
