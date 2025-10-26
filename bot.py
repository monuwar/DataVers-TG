import os
import random
import asyncio
import logging

# auto create name dataset if missing (kept as-is; harmless if present)
try:
    if not os.path.exists("names"):
        import name_dataset_builder  # noqa: F401
except Exception:
    pass

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

# ---------- Logging ----------
logging.basicConfig(level=logging.INFO)

# ---------- BOT SETUP ----------
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable missing!")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ---------- MAIN MENU ----------
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🧠 Name Generator"), KeyboardButton(text="📧 Email Generator")],
        [KeyboardButton(text="🗓️ OTP Mode"), KeyboardButton(text="🧩 Fake Data")],
        [KeyboardButton(text="➕ Plus Add"), KeyboardButton(text="🏠 Main Menu")],
    ],
    resize_keyboard=True,
)

gender_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Male"), KeyboardButton(text="Female")],
        [KeyboardButton(text="Mixed"), KeyboardButton(text="🏠 Main Menu")],
    ],
    resize_keyboard=True,
)

# ---------- USER CONTEXT ----------
user_state = {}
fake_sessions = {}

def reset_state(uid: int):
    user_state.pop(uid, None)
    fake_sessions.pop(uid, None)

# ---------- FILE LOADER (names) ----------
def load_names(country: str, gender: str):
    """Load names from one combined file per country-gender (First+Last same file)."""
    base = country.lower().replace(" ", "_")
    g = gender.lower()
    paths = [
        f"names/{base}_{g}.txt",
        f"names/{base}.txt",  # fallback
    ]
    for path in paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return [ln.strip() for ln in f if ln.strip()]
    return []

# ---------- /start ----------
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    reset_state(message.from_user.id)
    await message.answer("👋 Welcome to <b>DataVers TG Bot!</b>\n\nChoose an option below 👇", reply_markup=main_menu)

# ---------- Placeholder buttons (as-is) ----------
@dp.message(lambda m: m.text in ("📧 Email Generator", "🗓️ OTP Mode", "➕ Plus Add"))
async def other_features(message: types.Message):
    reset_state(message.from_user.id)
    await message.answer("🛠️ This feature is coming soon... stay tuned!")

# ---------- Main Menu ----------
@dp.message(lambda m: m.text == "🏠 Main Menu")
async def main_menu_back(message: types.Message):
    reset_state(message.from_user.id)
    await message.answer("🏠 Main Menu:\nSelect an option 👇", reply_markup=main_menu)

# ===========================
#        FAKE DATA FLOW
# ===========================
@dp.message(lambda m: m.text == "🧩 Fake Data")
async def fake_data_start(message: types.Message):
    uid = message.from_user.id
    fake_sessions[uid] = {"step": "country", "country": ""}
    await message.answer("🌍 Please type a country name (e.g. Bangladesh, Japan, USA)")

@dp.message(lambda m: m.from_user.id in fake_sessions and fake_sessions[m.from_user.id].get("step") == "country")
async def fake_data_country(message: types.Message):
    uid = message.from_user.id
    country = message.text.strip()
    fake_sessions[uid]["country"] = country
    fake_sessions[uid]["step"] = "gender"
    await message.answer(f"✅ Country selected: {country.title()}\n\nPlease select a gender:", reply_markup=gender_menu)

@dp.message(lambda m: m.from_user.id in fake_sessions and fake_sessions[m.from_user.id].get("step") == "gender")
async def fake_data_gender(message: types.Message):
    uid = message.from_user.id
    gender = message.text.strip().lower()
    if gender not in ["male", "female", "mixed"]:
        await message.answer("❌ Please select: Male / Female / Mixed", reply_markup=gender_menu)
        return
    fake_sessions[uid]["gender"] = gender
    fake_sessions[uid]["step"] = "count"
    await message.answer(f"🟢 Gender selected: {gender.title()}\n\n📊 How many fake data entries do you want?\n💡 Suggested: 10–50\n📈 Maximum: 5000\n\nPlease enter a number:")

@dp.message(lambda m: m.from_user.id in fake_sessions and fake_sessions[m.from_user.id].get("step") == "count")
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
    fake_sessions[uid]["step"] = "fields"
    await message.answer(
        "🧩 What fields do you want?\n👉 Send a comma-separated list, e.g. <code>first_name,last_name,age,city,phone,email</code>\n\n"
        "📋 Available fields:\n"
        "first_name, last_name, full_name, username, age, gender, city, state, country, postal_code, address, phone, email, job, company, uuid",
        parse_mode="HTML"
    )

from faker import Faker

@dp.message(lambda m: m.from_user.id in fake_sessions and fake_sessions[m.from_user.id].get("step") == "fields")
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
                    entry[f] = faker.first_name_male() if gender == "male" else faker.first_name_female() if gender == "female" else faker.first_name()
                elif f == "last_name":
                    entry[f] = faker.last_name()
                elif f == "full_name":
                    fn = faker.first_name_male() if gender == "male" else faker.first_name_female() if gender == "female" else faker.first_name()
                    entry[f] = f"{fn} {faker.last_name()}"
                elif f == "username":
                    entry[f] = faker.user_name()
                elif f == "age":
                    entry[f] = str(random.randint(18, 65))
                elif f == "gender":
                    entry[f] = gender.title() if gender in ("male", "female") else random.choice(["Male", "Female"])
                elif f == "city":
                    entry[f] = faker.city()
                elif f == "state":
                    entry[f] = faker.state()
                elif f == "country":
                    entry[f] = country.title()
                elif f == "postal_code":
                    entry[f] = faker.postcode()
                elif f == "address":
                    entry[f] = faker.address().replace("\n", ", ")
                elif f == "phone":
                    entry[f] = faker.phone_number()
                elif f == "email":
                    entry[f] = faker.email()
                elif f == "job":
                    entry[f] = faker.job()
                elif f == "company":
                    entry[f] = faker.company()
                elif f == "uuid":
                    entry[f] = faker.uuid4()
                else:
                    # unknown field name -> keep as empty/N/A
                    entry[f] = "N/A"
            except Exception:
                entry[f] = "N/A"
        data.append(entry)

    # Small preview for chat
    preview_lines = []
    show = min(10, len(data))
    for i in range(show):
        d = data[i]
        selected = [f"{k}: {v}" for k, v in d.items()]
        preview_lines.append(" • " + ", ".join(selected))
    preview = "\n".join(preview_lines)

    await message.answer(f"🎉 SUCCESS!\n✅ Generated {count} fake data entries for {country.title()}:\n\n{preview}")

    # If big – also attach as txt
    if count > 200:
        import io
        output = io.StringIO()
        for d in data:
            line = ", ".join([f"{k}: {v}" for k, v in d.items()])
            output.write(line + "\n")
        output.seek(0)
        await message.answer_document(
            types.InputFile(output, filename=f"{country.lower()}_fake_data.txt"),
            caption=f"📄 Generated {count} fake data entries for {country.title()}!"
        )

    fake_sessions.pop(uid, None)

# ===========================
#       NAME GENERATOR
# ===========================
@dp.message(lambda m: m.text == "🧠 Name Generator")
async def ask_country(message: types.Message):
    reset_state(message.from_user.id)
    user_state[message.from_user.id] = {"step": "country"}
    await message.answer("🌍 Type a country name (e.g. Bangladesh, India, Japan, USA)")

@dp.message(lambda m: user_state.get(m.from_user.id, {}).get("step") == "country")
async def got_country(message: types.Message):
    country = message.text.strip()
    user_state[message.from_user.id] = {"step": "gender", "country": country}
    await message.answer(f"✅ Country selected: {country.title()}\n\nPlease select a gender:", reply_markup=gender_menu)

@dp.message(lambda m: user_state.get(m.from_user.id, {}).get("step") == "gender")
async def got_gender(message: types.Message):
    g = message.text.strip().lower()
    if g not in ["male", "female", "mixed"]:
        await message.answer("❌ Please select: Male / Female / Mixed", reply_markup=gender_menu)
        return
    user_state[message.from_user.id]["gender"] = g
    user_state[message.from_user.id]["step"] = "count"
    await message.answer(f"🟢 Gender selected: {g.title()}\n\n📊 How many names do you want?\n💡 Suggested: 10–50\n📈 Maximum: 5000\n\nPlease enter a number:")

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

    # load names list
    names_list = load_names(country, gender)
    if not names_list:
        base = country.lower().replace(" ", "_")
        await message.answer(
            f"❌ No name data found for {country.title()} ({gender}).\n📄 Expected file: names/{base}_{gender}.txt or names/{base}.txt"
        )
        reset_state(uid)
        return

    # sample names
    if count > len(names_list):
        random.shuffle(names_list)
        result = names_list
    else:
        result = random.sample(names_list, count)

    # show in chat
    block = "\n".join(result)
    await message.answer(f"🎉 SUCCESS!\n✅ Generated {count} {gender.title()} names from {country.title()}:\n\n{block}")
    reset_state(uid)

# ---------- RUN ----------
async def main():
    logging.info("DataVers TG Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
