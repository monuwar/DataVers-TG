import os
import random
from faker import Faker
from faker.config import AVAILABLE_LOCALES

# 🌍 Full Global Faker Locale Map
# Faker লাইব্রেরিতে যতগুলো locale আছে — সব আমরা ব্যবহার করব
available_locales = AVAILABLE_LOCALES

# ✅ names ফোল্ডার তৈরি
os.makedirs("names", exist_ok=True)

def generate_dataset(locale_code, count=300):
    """Generate names for a specific locale"""
    fake = Faker(locale_code)
    names = []
    for _ in range(count):
        first = fake.first_name()
        last = fake.last_name()
        names.append(f"{first} {last}")
    return names

# 🔁 সব locale এর জন্য dataset বানানো
for loc in available_locales:
    safe_loc = loc.replace("-", "_").lower()
    for gender in ["male", "female"]:
        data = generate_dataset(loc, 300)
        file_path = f"names/{safe_loc}_{gender}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(data))

print(f"✅ All global name datasets generated successfully for {len(available_locales)} locales 🌍")
