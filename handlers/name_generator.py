from aiogram import Router, F
from aiogram.types import Message
from faker import Faker
import re

router = Router()

# per-user simple state (very light)
USER_STATE = {}

# Supported locales
COUNTRY_LOCALES = {
    "Norway": "no_NO",
    "United States": "en_US",
    "Bangladesh": "en_US",
    "India": "en_IN",
    "Germany": "de_DE",
    "France": "fr_FR",
    "Japan": "ja_JP",
}

# case-insensitive regex for country detection
COUNTRY_PATTERN = re.compile(
    r"^(?i)(norway|united states|bangladesh|india|germany|france|japan)$"
)

@router.message(F.text == "👤 Name Generator")
async def ng_start(message: Message):
    txt = (
        "🌍 **Name Generator Activated!**\n"
        "Choose a country (type one):\n\n"
        "Norway, United States, Bangladesh, India, Germany, France, Japan"
    )
    USER_STATE.pop(message.from_user.id, None)  # reset flow for this user
    await message.answer(txt, parse_mode="Markdown")

# 1) Country
@router.message(F.text.regexp(COUNTRY_PATTERN))
async def ng_country(message: Message):
    country = message.text.strip().title()
    USER_STATE[message.from_user.id] = {"country": country}
    await message.answer(
        f"✅ Country selected: {country}\n\nPlease type gender:\n- Male\n- Female\n- Mixed"
    )

# 2) Gender
@router.message(F.text.regexp(r"^(?i)(male|female|mixed)$"))
async def ng_gender(message: Message):
    uid = message.from_user.id
    if uid not in USER_STATE or "country" not in USER_STATE[uid]:
        return  # user didn't start flow; ignore silently
    gender = message.text.strip().capitalize()
    USER_STATE[uid]["gender"] = gender
    await message.answer("📊 How many names do you want? (e.g., 10, 50, 100; max 5000)")

# 3) Count and generate
@router.message(F.text.regexp(r"^\d+$"))
async def ng_generate(message: Message):
    uid = message.from_user.id
    if uid not in USER_STATE or "country" not in USER_STATE[uid] or "gender" not in USER_STATE[uid]:
        return  # not in flow
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

    # small output inline; big output as file
    if count <= 100:
        text = f"🎉 Generated {count} {gender.lower()} names from {country}:\n\n" + "\n".join(names)
        await message.answer(text)
    else:
        filename = f"names_{country.lower().replace(' ', '_')}_{gender.lower()}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(names))
        await message.answer_document(open(filename, "rb"),
                                      caption=f"🎉 {count} names from {country}")

    # done → clear state
    USER_STATE.pop(uid, None)
