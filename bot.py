from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from faker import Faker
import re
import time
import os

router = Router()

# ===== USER SESSION =====
USER_STATE = {}

# ===== SUPPORTED LOCALES =====
COUNTRY_LOCALES = {
    "Norway": "no_NO",
    "United States": "en_US",
    "Bangladesh": "en_US",  # placeholder — later custom dataset
    "India": "en_IN",
    "Germany": "de_DE",
    "France": "fr_FR",
    "Japan": "ja_JP"
}

# ===== COUNTRY DETECTION REGEX =====
COUNTRY_PATTERN = re.compile(r"(?i)^(norway|united states|bangladesh|india|germany|france|japan)$")

# ===== 1️⃣ START COMMAND =====
@router.message(F.text.regexp(r"(?i)(name\s*generator)"))
async def ng_start(message: Message):
    text = (
        "🌐 <b>Name Generator Activated!</b>\n\n"
        "Choose a country (type one):\n"
        "Norway, United States, Bangladesh, India, Germany, France, Japan"
    )
    USER_STATE.pop(message.from_user.id, None)
    await message.answer(text, parse_mode="HTML")

# ===== 2️⃣ COUNTRY SELECTION =====
@router.message(F.text.regexp(COUNTRY_PATTERN))
async def ng_country(message: Message):
    country = message.text.strip().title()
    USER_STATE[message.from_user.id] = {"country": country}
    await message.answer(
        f"✅ Country selected: <b>{country}</b>\n\n"
        "Please type gender:\n"
        "- Male\n"
        "- Female\n"
        "- Mixed",
        parse_mode="HTML"
    )

# ===== 3️⃣ GENDER SELECTION =====
@router.message(F.text.regexp(r"(?i)^(male|female|mixed)$"))
async def ng_gender(message: Message):
    uid = message.from_user.id
    if uid not in USER_STATE or "country" not in USER_STATE[uid]:
        return
    gender = message.text.strip().capitalize()
    USER_STATE[uid]["gender"] = gender
    await message.answer("📊 How many names do you want? (e.g., 10, 50, 100; max 5000)")

# ===== 4️⃣ GENERATE NAMES =====
@router.message(F.text.regexp(r"^\d+$"))
async def ng_generate(message: Message):
    uid = message.from_user.id
    if uid not in USER_STATE or "gender" not in USER_STATE[uid]:
        return

    count = int(message.text)
    if count > 5000:
        await message.answer("❌ Maximum allowed is 5000 names.")
        return

    country = USER_STATE[uid]["country"]
    gender = USER_STATE[uid]["gender"]
    locale = COUNTRY_LOCALES.get(country, "en_US")
    fake = Faker(locale)

    names = []
    for _ in range(count):
        if gender == "Male":
            names.append(f"{fake.first_name_male()} {fake.last_name()}")
        elif gender == "Female":
            names.append(f"{fake.first_name_female()} {fake.last_name()}")
        else:
            names.append(fake.name())

    # ===== 5️⃣ OUTPUT HANDLING =====
    if count <= 200:
        text = (
            f"🎉 <b>Generated {count} {gender.lower()} names from {country}:</b>\n\n"
            + "\n".join(names)
        )
        await message.answer(text, parse_mode="HTML")
    else:
        safe_country = country.lower().replace(" ", "_")
        filename = f"names_{safe_country}_{int(time.time())}.txt"

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(names))

        try:
            document = FSInputFile(filename)
            await message.answer_document(
                document=document,
                caption=(
                    f"✅ Generated {count} {gender.lower()} names from {country}\n"
                    "📄 File ready for download!"
                ),
            )
        except Exception as e:
            await message.answer(f"⚠️ File sending failed:\n{e}")
        finally:
            if os.path.exists(filename):
                os.remove(filename)

    # ===== 6️⃣ CLEAR USER SESSION =====
    USER_STATE.pop(uid, None)
