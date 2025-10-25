from aiogram import Router, F
from aiogram.types import Message
from faker import Faker

router = Router()
fake = Faker()

COUNTRY_LOCALES = {
    "Norway": "no_NO",
    "United States": "en_US",
    "Bangladesh": "en_US",
    "India": "en_IN",
    "Germany": "de_DE",
    "France": "fr_FR",
    "Japan": "ja_JP"
}

@router.message(F.text == "👤 Name Generator")
async def ask_country(message: Message):
    text = (
        "🌍 **Name Generator Activated!**\n"
        "Choose a country:\n\n"
        "Supported examples: Norway, United States, Bangladesh, India, Germany, France, Japan"
    )
    await message.answer(text, parse_mode="Markdown")

@router.message(F.text.in_(COUNTRY_LOCALES.keys()))
async def ask_gender(message: Message):
    message.bot['user_country'] = message.text
    await message.answer(
        f"✅ Country selected: {message.text}\n\nPlease select gender:\n"
        "- Male\n- Female\n- Mixed"
    )

@router.message(F.text.in_(["Male", "Female", "Mixed"]))
async def ask_count(message: Message):
    message.bot['user_gender'] = message.text
    await message.answer("📊 How many names do you want to generate? (e.g., 10, 50, 100)")

@router.message(F.text.regexp(r"^\d+$"))
async def generate_names(message: Message):
    try:
        count = int(message.text)
        if count > 5000:
            return await message.answer("❌ Maximum allowed is 5000 names.")

        gender = message.bot.get('user_gender', 'Mixed')
        country = message.bot.get('user_country', 'United States')
        locale = COUNTRY_LOCALES.get(country, "en_US")
        fake = Faker(locale)

        names = []
        for _ in range(count):
            if gender == "Male":
                names.append(fake.first_name_male() + " " + fake.last_name())
            elif gender == "Female":
                names.append(fake.first_name_female() + " " + fake.last_name())
            else:
                names.append(fake.name())

        if count <= 100:
            text = f"🎉 Generated {count} {gender.lower()} names from {country}:\n\n" + "\n".join(names)
            await message.answer(text)
        else:
            filename = f"names_{country.lower()}_{gender.lower()}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write("\n".join(names))
            await message.answer_document(open(filename, "rb"), caption=f"🎉 {count} names from {country}")

    except Exception as e:
        await message.answer(f"⚠️ Error: {e}")
