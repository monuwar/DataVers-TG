import os
import random
from faker import Faker

print("🌍 Starting global name dataset build...")

# সব দেশের fallback সহ dataset বানানোর জন্য
faker = Faker()
locales = faker.locales

# Output folder
os.makedirs("names", exist_ok=True)

# Country alias system (common inputs)
aliases = {
    "usa": "en_US",
    "us": "en_US",
    "uk": "en_GB",
    "uae": "ar_AE",
    "sa": "ar_SA",
    "jp": "ja_JP",
    "kr": "ko_KR",
    "cn": "zh_CN",
    "in": "en_IN",
    "bd": "bn_BD",
    "br": "pt_BR",
    "fr": "fr_FR",
    "de": "de_DE",
    "it": "it_IT",
    "es": "es_ES",
    "pk": "ur_PK",
    "ru": "ru_RU",
    "ir": "fa_IR",
}

# সকল Locale list (যা Faker সাপোর্ট করে)
supported_locales = set(locales)

# দেশ fallback system
def get_locale(country_name: str):
    c = country_name.strip().lower()
    if c in aliases:
        return aliases[c]
    match = [loc for loc in supported_locales if c in loc.lower() or loc.lower() in c]
    if match:
        return match[0]
    return "en_US"

# 180+ দেশের dataset তৈরি
countries = [
    "bangladesh", "india", "pakistan", "usa", "uk", "japan", "china", "russia", "brazil",
    "argentina", "france", "germany", "italy", "spain", "portugal", "canada", "australia",
    "uae", "saudi arabia", "egypt", "turkey", "indonesia", "malaysia", "thailand", "vietnam",
    "nepal", "sri lanka", "south korea", "north korea", "iran", "iraq", "afghanistan",
    "mexico", "chile", "colombia", "peru", "nigeria", "kenya", "ethiopia", "south africa",
    "poland", "sweden", "norway", "finland", "denmark", "switzerland", "netherlands",
    "belgium", "austria", "czech republic", "romania", "hungary", "greece", "israel",
    "singapore", "philippines", "myanmar", "qatar", "kuwait", "oman", "yemen", "morocco",
    "algeria", "sudan", "tunisia", "libya", "lebanon", "jordan", "palestine", "new zealand",
    "iceland", "ireland", "croatia", "serbia", "bulgaria", "slovakia", "slovenia", "latvia",
    "lithuania", "estonia", "azerbaijan", "georgia", "kazakhstan", "uzbekistan", "turkmenistan",
    "armenia", "belarus", "ukraine", "venezuela", "paraguay", "bolivia", "uruguay", "haiti",
    "cuba", "dominican republic", "panama", "costarica", "honduras", "guatemala", "el salvador",
    "nicaragua", "bahrain"
]

# ডেটা তৈরি
count = 0
for country in countries:
    loc = get_locale(country)
    f = Faker(loc)
    for gender in ["male", "female"]:
        names = []
        for _ in range(500):
            name = f.name()
            names.append(name)
        file_path = f"names/{country.lower()}_{gender}.txt"
        with open(file_path, "w", encoding="utf-8") as f_out:
            f_out.write("\n".join(names))
        count += 1

print(f"✅ All global name datasets generated successfully for {len(countries)} countries 🌎")
print(f"📁 Total files created: {count}")
print("⚙️ Auto fallback enabled for missing locales (uses en_US).")
