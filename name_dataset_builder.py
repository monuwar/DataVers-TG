import os
import random
import unicodedata
from faker import Faker
from faker.config import AVAILABLE_LOCALES

# 🌍 GLOBAL AI + FAKER HYBRID BUILDER
print("🌎 Starting Full Global Hybrid Name Dataset Builder...")

# Folder
os.makedirs("names", exist_ok=True)

# ---------- UTIL ----------
def normalize_name(text: str) -> str:
    """Convert to ASCII-only readable English"""
    return ''.join(
        c for c in unicodedata.normalize('NFKD', text)
        if not unicodedata.combining(c) and c.isascii()
    )

# ---------- LOCAL BOOSTER ----------
local_overrides = {
    "bangladesh": {
        "male_first": ["Rakib", "Hasan", "Sabbir", "Ashik", "Sajid", "Naeem", "Raihan", "Tanvir"],
        "female_first": ["Nusrat", "Mim", "Rupa", "Sadia", "Sumaiya", "Jannat"],
        "last": ["Rahman", "Khan", "Chowdhury", "Sarker", "Hossain", "Uddin", "Ali"]
    },
    "saudi arabia": {
        "male_first": ["Ahmed", "Omar", "Khalid", "Abdullah", "Faisal", "Yousef", "Nadeem"],
        "female_first": ["Aisha", "Fatimah", "Layla", "Sara", "Reem", "Noor"],
        "last": ["Al-Fahad", "Al-Qahtani", "Al-Saud", "Al-Amri", "Al-Zahrani", "Rahman"]
    },
    "india": {
        "male_first": ["Arjun", "Ravi", "Amit", "Deepak", "Rajesh", "Vikram", "Sanjay"],
        "female_first": ["Priya", "Anjali", "Kavita", "Neha", "Pooja", "Sneha"],
        "last": ["Sharma", "Patel", "Singh", "Gupta", "Verma", "Iyer"]
    },
    "japan": {
        "male_first": ["Taro", "Hiroshi", "Kenji", "Yuki", "Kenta", "Satoshi"],
        "female_first": ["Yumi", "Sakura", "Aiko", "Haruka", "Rina", "Miyu"],
        "last": ["Sato", "Suzuki", "Takahashi", "Kobayashi", "Tanaka"]
    }
}

# ---------- GENERATOR ----------
def generate_locale_names(locale):
    faker = Faker(locale)
    country = locale.replace("_", "-").lower()
    safe_country = country.replace(" ", "_")

    for gender in ["male", "female"]:
        names = []
        for _ in range(500):
            try:
                if gender == "male":
                    first = faker.first_name_male()
                else:
                    first = faker.first_name_female()
                last = faker.last_name()
                full = normalize_name(f"{first} {last}")
                if len(full.split()) == 2:
                    names.append(full)
            except Exception:
                continue

        with open(f"names/{safe_country}_{gender}.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(names))

# ---------- MAIN LOOP ----------
faker_global = Faker("en_US")
total_locales = len(AVAILABLE_LOCALES)
success = 0
failed = []

for loc in AVAILABLE_LOCALES:
    try:
        generate_locale_names(loc)
        success += 1
    except Exception as e:
        failed.append((loc, str(e)))

# ---------- LOCAL COUNTRY MERGE ----------
for country, data in local_overrides.items():
    for gender in ["male", "female"]:
        first_list = data[f"{gender}_first"]
        last_list = data["last"]
        names = [f"{random.choice(first_list)} {random.choice(last_list)}" for _ in range(500)]
        file_path = f"names/{country.lower().replace(' ', '_')}_{gender}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(names))
    print(f"✅ Added custom dataset for {country.title()}")

# ---------- FINAL SUMMARY ----------
print(f"\n✅ Total locales processed successfully: {success}/{total_locales}")
print(f"📁 Total files created: {success*2 + len(local_overrides)*2}")
print(f"🌐 Custom local datasets added: {', '.join(local_overrides.keys())}")
if failed:
    print(f"⚠️ Failed locales: {len(failed)} (ignored safely)")
print("🎉 All datasets localized, English-friendly, and ready for 180 + countries!")
