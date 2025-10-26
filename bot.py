import os
import random
import asyncio
import logging
from faker import Faker
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN missing!")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
faker = Faker()

# ---------- MAIN INLINE MENU ----------
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧠 Name Generator", callback_data="menu_name"),
         InlineKeyboardButton(text="🧩 Fake Data", callback_data="menu_fake")],
        [InlineKeyboardButton(text="📧 Email Generator", callback_data="menu_email"),
         InlineKeyboardButton(text="🔢 OTP Mode", callback_data="menu_otp")],
    ])

# ---------- START COMMAND ----------
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "👋 <b>Welcome to DataVers TG Bot!</b>\n\nChoose an option below 👇",
        reply_markup=main_menu()
    )

# ---------- MAIN MENU CALLBACK ----------
@dp.callback_query(F.data == "home")
async def go_home(cb: types.CallbackQuery):
    await cb.message.edit_text(
        "🏠 <b>Main Menu</b>\nSelect an option 👇",
        reply_markup=main_menu()
    )
    await cb.answer()

# ========== 🧠 NAME GENERATOR ==========
from aiogram.utils.keyboard import InlineKeyboardBuilder

def gender_menu(prefix):
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="♂️ Male", callback_data=f"{prefix}_male"),
        InlineKeyboardButton(text="♀️ Female", callback_data=f"{prefix}_female"),
        InlineKeyboardButton(text="⚧️ Mixed", callback_data=f"{prefix}_mixed")
    )
    kb.row(InlineKeyboardButton(text="🏠 Main Menu", callback_data="home"))
    return kb.as_markup()

@dp.callback_query(F.data == "menu_name")
async def name_start(cb: types.CallbackQuery):
    await cb.message.edit_text("🌍 Type a country name (e.g. Bangladesh, India, Japan):")
    dp["state"] = {"mode": "name_country"}
    await cb.answer()

@dp.message(lambda m: dp.get("state", {}).get("mode") == "name_country")
async def name_country(msg: types.Message):
    dp["state"] = {"mode": "name_gender", "country": msg.text.strip()}
    await msg.answer(f"✅ Country selected: {msg.text.title()}\n\nSelect gender:", reply_markup=gender_menu("name"))

@dp.callback_query(F.data.startswith("name_"))
async def name_gender(cb: types.CallbackQuery):
    gender = cb.data.split("_")[1]
    country = dp.get("state", {}).get("country", "Unknown")
    count = 10
    names = []
    for _ in range(count):
        if gender == "male":
            names.append(faker.first_name_male())
        elif gender == "female":
            names.append(faker.first_name_female())
        else:
            names.append(faker.first_name())
    result = "\n".join(names)
    await cb.message.edit_text(
        f"🎉 <b>{count} {gender.title()} Names</b> from {country.title()}:\n\n{result}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton("🏠 Main Menu", callback_data="home")]])
    )
    dp["state"] = {}
    await cb.answer()

# ========== 🧩 FAKE DATA GENERATOR ==========
def fake_gender_menu():
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="♂️ Male", callback_data="fake_male"),
        InlineKeyboardButton(text="♀️ Female", callback_data="fake_female"),
        InlineKeyboardButton(text="⚧️ Mixed", callback_data="fake_mixed")
    )
    kb.row(InlineKeyboardButton(text="🏠 Main Menu", callback_data="home"))
    return kb.as_markup()

@dp.callback_query(F.data == "menu_fake")
async def fake_start(cb: types.CallbackQuery):
    dp["state"] = {"mode": "fake_country"}
    await cb.message.edit_text("🌍 Type a country name for fake data:")
    await cb.answer()

@dp.message(lambda m: dp.get("state", {}).get("mode") == "fake_country")
async def fake_country(msg: types.Message):
    dp["state"] = {"mode": "fake_gender", "country": msg.text.strip()}
    await msg.answer(f"✅ Country: {msg.text.title()}\nSelect gender:", reply_markup=fake_gender_menu())

@dp.callback_query(F.data.startswith("fake_"))
async def fake_gender(cb: types.CallbackQuery):
    gender = cb.data.split("_")[1]
    country = dp.get("state", {}).get("country", "Unknown")
    profiles = []
    for _ in range(5):
        fn = faker.first_name_male() if gender == "male" else faker.first_name_female() if gender == "female" else faker.first_name()
        ln = faker.last_name()
        profiles.append(
            f"👤 {fn} {ln}\n📧 {faker.email()}\n📞 {faker.phone_number()}\n🏙️ {faker.city()}, {country.title()}\n💼 {faker.job()}"
        )
    text = "\n\n".join(profiles)
    await cb.message.edit_text(
        f"🎉 <b>Generated 5 {gender.title()} Fake Profiles</b> for {country.title()}:\n\n{text}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton("🏠 Main Menu", callback_data="home")]])
    )
    dp["state"] = {}
    await cb.answer()

# ========== 🏠 NAVIGATION (Already linked to Main Menu) ==========
# "home" callback already handled above.

# ========== 📧 EMAIL GENERATOR ==========
@dp.callback_query(F.data == "menu_email")
async def email_gen(cb: types.CallbackQuery):
    emails = []
    for _ in range(10):
        fn = faker.first_name().lower()
        ln = faker.last_name().lower()
        domain = random.choice(["gmail.com", "yahoo.com", "outlook.com", "proton.me"])
        emails.append(f"{fn}.{ln}@{domain}")
    result = "\n".join(emails)
    await cb.message.edit_text(
        f"📧 <b>Sample Email Addresses</b>:\n\n{result}",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton("🏠 Main Menu", callback_data="home")]]
        )
    )
    await cb.answer()

# ========== 🔢 OTP MODE ==========
@dp.callback_query(F.data == "menu_otp")
async def otp_mode(cb: types.CallbackQuery):
    otp = random.randint(100000, 999999)
    await cb.message.edit_text(
        f"🔢 <b>Generated OTP:</b> <code>{otp}</code>\n⌛ Valid for 1 minute!",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton("🏠 Main Menu", callback_data="home")]]
        )
    )
    await cb.answer()
    await asyncio.sleep(60)
    try:
        await cb.message.edit_text("⌛ OTP Expired! ⚠️", reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton("🏠 Main Menu", callback_data="home")]]
        ))
    except Exception:
        pass

# ========== 🚀 RUN BOT ==========
async def main():
    print("🚀 DataVers TG Inline Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

