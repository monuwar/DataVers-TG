import os
import random

# -----------------------------
# 🌍 ১. দেশের নামের তালিকা
# -----------------------------
countries = {
    "bangladesh": {
        "male_first": ["Rashid", "Hussain", "Ibrahim", "Yusuf", "Bilal", "Farid", "Sajid", "Nayeem", "Rafi", "Arif"],
        "female_first": ["Mariam", "Ayesha", "Jannat", "Farzana", "Sadia", "Sumaiya", "Runa", "Lamia", "Nusrat", "Jahanara"],
        "last": ["Chowdhury", "Siddique", "Miah", "Ali", "Rahman", "Hassan", "Khan", "Uddin", "Ahmed", "Mollah"]
    },
    "india": {
        "male_first": ["Ravi", "Amit", "Suresh", "Rajesh", "Manish", "Deepak", "Rahul", "Sanjay", "Vikram", "Anil"],
        "female_first": ["Priya", "Anjali", "Kavita", "Neha", "Pooja", "Ritu", "Swati", "Meena", "Sonia", "Lata"],
        "last": ["Patel", "Sharma", "Gupta", "Singh", "Mehta", "Iyer", "Verma", "Reddy", "Naidu", "Kapoor"]
    },
    "usa": {
        "male_first": ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Charles", "Thomas"],
        "female_first": ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Susan", "Jessica", "Sarah", "Karen", "Nancy"],
        "last": ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    },
    "japan": {
        "male_first": ["Hiroshi", "Takashi", "Taro", "Yuki", "Kenta", "Shinji", "Naoki", "Ryo", "Kazuya", "Sota"],
        "female_first": ["Yumi", "Sakura", "Aiko", "Haruka", "Rina", "Mika", "Asuka", "Emi", "Aya", "Nana"],
        "last": ["Tanaka", "Suzuki", "Takahashi", "Sato", "Kobayashi", "Watanabe", "Ito", "Yamamoto", "Nakamura", "Kato"]
    }
}

# -----------------------------
# 📁 ২. ফোল্ডার তৈরি
# -----------------------------
os.makedirs("names", exist_ok=True)

# -----------------------------
# 🧠 ৩. ডাটা ফাইল জেনারেশন
# -----------------------------
for country, data in countries.items():
    for gender in ["male", "female"]:
        first_names = data[f"{gender}_first"]
        last_names = data["last"]

        # একত্রে নাম তৈরি করা
        combined = [f"{fn} {ln}" for fn in first_names for ln in random.sample(last_names, len(last_names)//2)]

        # ফাইল লিখে ফেলা
        file_path = f"names/{country}_{gender}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(combined))

print("✅ All dataset files generated successfully inside /names folder!")
