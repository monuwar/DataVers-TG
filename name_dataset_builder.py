import os
import random
from faker import Faker

print("🌍 Starting AI + Faker Hybrid Global Name Builder (English Mode with Localized Firstnames)...")

os.makedirs("names", exist_ok=True)

# 🌎 Country → locale + firstname + lastname mapping
locale_map = {
    "bangladesh": {
        "locale": "en_US",
        "first": ["Rakib", "Asif", "Tareq", "Nayeem", "Arif", "Sajid", "Sohan", "Rashed", "Mamun", "Fahim", "Hasan", "Sabbir", "Noman", "Saiful"],
        "last": ["Rahman", "Miah", "Chowdhury", "Khan", "Uddin", "Hossain", "Ali", "Sarker"]
    },
    "india": {
        "locale": "en_IN",
        "first": ["Amit", "Ravi", "Suresh", "Rajesh", "Arjun", "Vikram", "Deepak", "Manish", "Karan", "Rohit"],
        "last": ["Patel", "Sharma", "Gupta", "Kumar", "Reddy", "Das", "Iyer"]
    },
    "pakistan": {
        "locale": "en_US",
        "first": ["Ahmed", "Ali", "Hassan", "Faisal", "Bilal", "Zain", "Imran", "Usman"],
        "last": ["Khan", "Raza", "Qureshi", "Malik", "Hussain"]
    },
    "usa": {
        "locale": "en_US",
        "first": [],
        "last": ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller"]
    },
    "uk": {
        "locale": "en_GB",
        "first": [],
        "last": ["Taylor", "Evans", "King", "Wright", "Baker"]
    },
    "japan": {
        "locale": "en_US",
        "first": ["Taro", "Yuki", "Kenta", "Ryo", "Haruto"],
        "last": ["Sato", "Suzuki", "Takahashi", "Tanaka", "Watanabe"]
    },
    "italy": {
        "locale": "en_US",
        "first": ["Luca", "Marco", "Matteo", "Alessandro", "Giovanni"],
        "last": ["Rossi", "Russo", "Ferrari", "Esposito"]
    },
    "france": {
        "locale": "en_US",
        "first": ["Pierre", "Louis", "Hugo", "Lucas", "Julien"],
        "last": ["Dubois", "Lefevre", "Moreau", "Laurent"]
    },
    "spain": {
        "locale": "en_US",
        "first": ["Carlos", "Miguel", "Juan", "Jose", "Antonio"],
        "last": ["Garcia", "Martinez", "Rodriguez", "Lopez"]
    },
    "brazil": {
        "locale": "en_US",
        "first": ["Joao", "Pedro", "Lucas", "Mateus", "Rafael"],
        "last": ["Silva", "Santos", "Oliveira", "Souza"]
    },
}

faker = Faker()

# 🧠 Generate names per country
def generate_names(country, data):
    locale = data["locale"]
    f = Faker(locale)
    first_list = data["first"]
    last_list = data["last"]
    all_names = []
    for gender in ["male", "female"]:
        names = []
        for _ in range(500):
            if first_list:
                first = random.choice(first_list)
            else:
                first = f.first_name_male() if gender == "male" else f.first_name_female()
            first = ''.join(c for c in first if c.isascii())
            last = random.choice(last_list)
            names.append(f"{first} {last}")
        with open(f"names/{country}_{gender}.txt", "w", encoding="utf-8") as f_out:
            f_out.write("\n".join(names))
        all_names += names
    return all_names

count = 0
for country, data in locale_map.items():
    try:
        generate_names(country, data)
        count += 2
    except Exception as e:
        print(f"⚠️ Failed for {country}: {e}")

print(f"\n✅ Total countries processed: {len(locale_map)}")
print(f"📁 Total files created: {count}")
print("🌎 All names are in English with local realistic first + last name combos.")
