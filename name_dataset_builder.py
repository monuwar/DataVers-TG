import os
import random
from faker import Faker
from faker.config import AVAILABLE_LOCALES

# 🌍 Full Global Locale List (Faker থেকে সব locale)
available_locales = [loc.lower().replace("-", "_") for loc in AVAILABLE_LOCALES]

# ✅ ফোল্ডার তৈরি
os.makedirs("names", exist_ok=True)

# ⚙️ Dataset জেনারেটর
def generate_dataset(locale_code, count=300):
    """Generate names for a specific locale safely with fallback."""
    try:
        fake = Faker(locale_code)
        names = [f"{fake.first_name()} {fake.last_name()}" for _ in range(count)]
        return names
    except Exception:
        # 🔄 যদি locale কাজ না করে, fallback to English (USA)
        fake = Faker("en_US")
        names = [f"{fake.first_name()} {fake.last_name()}" for _ in range(count)]
        return names

# 🔁 সব দেশের জন্য dataset তৈরি
generated = 0
for loc in available_locales:
    for gender in ["male", "female"]:
        data = generate_dataset(loc, 300)
        file_path = f"names/{loc}_{gender}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(data))
        generated += 1

print(f"✅ All global name datasets generated successfully for {len(available_locales)} locales 🌍")
print(f"📁 Total files created: {generated}")
print("⚙️ Auto fallback enabled for missing locales (uses en_US).")
