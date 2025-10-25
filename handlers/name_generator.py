from aiogram import Router, F
from aiogram.types import Message
from faker import Faker
import time
import re

router = Router()

# User session state
USER_STATE = {}

# Supported locales
COUNTRY_LOCALES = {
    "Norway": "no_NO",
    "United States": "en_US",
    "Bangladesh": "en_US",  # later: custom dataset
    "India": "en_IN",
    "Germany": "de_DE",
    "France": "fr_FR",
    "Japan": "ja_JP"
}

# Regex for detecting country
COUNTRY_PATTERN = re.compile(r"(?i)^(norway|united states|bangladesh|india|germany|france|japan)$")

@router.message(F.text == "👤 Name Generator")
async def ng_start(message: Message):
    text = (
        "🌍 **Name Generator Activated!**\n\n"
        "Choose a country (type one):\n"
        "Norway, United States, Bangladesh, India, Germany, France, Japan"
    )
    USER_STATE.pop(message.from_user.id, None)
    await message.answer(text, parse_mode="Markdown")

# Step 1: Country select
@router.message(F.text.regexp(COUNTRY_PATTERN))
async def ng_country(message: Message):
    country = message.text.strip().title()
    USER_STATE[message.from_user.id] = {"country": country}
    await message.answer(
        f"✅ Country selected: {country}\n\nPlease type gender:\n- Male\n- Female\n- Mixed"
    )

# Step 2: Gender select
@router.message(F.text.regexp(r"(?i)^(male|female|mixed)$"))
async def ng_gender(message: Message):
    uid = message.from_user.id
    if uid not in USER_STATE or "country" not in USER_STATE[uid]:
        return
    gender = message.text.strip().capitalize()
    USER_STATE[uid]["gender"] = gender
    await message.answer("📊 How many names do you want? (e.g., 10, 50, 100; max 5000)")

# Step 3: Name count and generate
@router.message(F.text.regexp(r"^\d+$"))
async def ng_generate(message: Message):
    uid = message.from_user.id
    if uid not in USER_STATE or "gender" not in USER_STATE[uid]:
        return

    count = int(message.text)
    if count > 5000:
        return await message.answer("❌ Maximum allowed is 5000 names.")

    country = USER_STATE[uid]["country"]
    gender = USER_STATE[uid]["gender"]
    fake = Faker(COUNTRY_LOCALES.get(country, "en_US"))

    names = []
    for _ in range(count):
        if gender == "Male":
            names.append(f"{fake.first_name_male()} {fake.last_name()}")
        elif gender == "Female":
            names.append(f"{fake.first_name_female()} {fake.last_name()}")
        else:
            names.append(fake.name())

    from aiogram.types import FSInputFile

from aiogram.types import FSInputFile

# 🧩 Output Fix: ≤200 in chat, >200 as file
if count <= 200:
    text = f"🎉 Generated {count} {gender.lower()} names from {country}:\n\n" + "\n".join(names)
    await message.answer(text)
else:
    safe_country = country.lower().replace(" ", "_")
    filename = f"names_{safe_country}_{int(time.time())}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(names))

    try:
        document = FSInputFile(filename)
        await message.answer_document(
            document=document,
            caption=f"✅ Generated {count} {gender.lower()} names from {country}\n📄 File ready for download!"
        )
    except Exception as e:
        await message.answer(f"⚠️ File sending failed:\n{e}")

USER_STATE.pop(uid, None)
