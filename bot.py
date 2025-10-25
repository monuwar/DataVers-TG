import os
import random
import asyncio
import logging
from typing import List

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable missing!")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ---------------- UI (Reply Keyboard - unchanged) ----------------
MENU_BTNS = [
    "🧠 Name Generator", "📧 Email Generator",
    "🔢 OTP Mode", "🧩 Fake Data",
    "➕ Plus Add", "🏠 Main Menu"
]
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🧠 Name Generator"), KeyboardButton(text="📧 Email Generator")],
        [KeyboardButton(text="🔢 OTP Mode"), KeyboardButton(text="🧩 Fake Data")],
        [KeyboardButton(text="➕ Plus Add"), KeyboardButton(text="🏠 Main Menu")]
    ],
    resize_keyboard=True
)

GENDER_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Male"), KeyboardButton(text="Female")],
        [KeyboardButton(text="Mixed"), KeyboardButton(text="🏠 Main Menu")]
    ],
    resize_keyboard=True
)

# --------------- Simple in-memory context ---------------
CTX = {}  # {user_id: {"step": "country|gender|count", "country": str, "gender": str}}

def reset_ctx(uid: int):
    CTX.pop(uid, None)

# --------------- Files Loader (flexible) ---------------
NAMES_DIR = "names"

def read_lines(path: str) -> List[str]:
    if not os.path.exists(path): 
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip()]

def load_first_last(country: str, gender: str):
    """Try multiple naming schemes. Return (first_list, last_list)."""
    c = country.lower()
    g = gender.lower()

    # 1) names/{country}_{gender}_first.txt + names/{country}_{gender}_last.txt
    first = read_lines(os.path.join(NAMES_DIR, f"{c}_{g}_first.txt"))
    last  = read_lines(os.path.join(NAMES_DIR, f"{c}_{g}_last.txt"))
    if first and last: return first, last

    # 2) names/{country}_{gender}.txt (first) + names/{country}_surnames.txt (last)
    first = read_lines(os.path.join(NAMES_DIR, f"{c}_{g}.txt"))
    last  = read_lines(os.path.join(NAMES_DIR, f"{c}_surnames.txt"))
    if first and last: return first, last

    # 3) names/{country}_first.txt + names/{country}_last.txt
    first = read_lines(os.path.join(NAMES_DIR, f"{c}_first.txt"))
    last  = read_lines(os.path.join(NAMES_DIR, f"{c}_last.txt"))
    if first and last: return first, last

    # 4) Fallback: names/{country}_{gender}.txt for both (not ideal but works)
    both = read_lines(os.path.join(NAMES_DIR, f"{c}_{g}.txt"))
    if len(both) >= 2: return both, both

    # 5) Final fallback: names/{country}.txt for both
    both = read_lines(os.path.join(NAMES_DIR, f"{c}.txt"))
    if len(both) >= 2: return both, both

    return [], []

def combo(first_list: List[str], last_list: List[str], n: int) -> List[str]:
    res = []
    for _ in range(n):
        res.append(f"{random.choice(first_list)} {random.choice(last_list)}")
    return res

# ----------------- START -----------------
@dp.message(CommandStart())
async def start_cmd(m: types.Message):
    reset_ctx(m.from_user.id)
    await m.answer("👋 Welcome to <b>DataVers TG Bot</b>!\n\nChoose an option below 👇", reply_markup=main_menu)

# ----------------- HIGH-PRIORITY MAIN BUTTONS (always reset) -----------------
@dp.message(F.text.in_(btn for btn in MENU_BTNS if btn != "🧠 Name Generator"))
async def other_main_buttons(m: types.Message):
    # pressing any other main button cancels flows safely
    reset_ctx(m.from_user.id)
    await m.answer("⚙️ This feature is coming soon... stay tuned!" if m.text != "🏠 Main Menu"
                   else "🏠 Main Menu:\nSelect an option 👇", reply_markup=main_menu)

# ----------------- NAME GENERATOR FLOW -----------------
@dp.message(F.text == "🧠 Name Generator")
async def namegen_start(m: types.Message):
    reset_ctx(m.from_user.id)
    CTX[m.from_user.id] = {"step": "country"}
    await m.answer("🌍 Type a country name (e.g. Bangladesh, India, Japan, USA)")

@dp.message(lambda msg: CTX.get(msg.from_user.id, {}).get("step") == "country")
async def step_country(m: types.Message):
    country = m.text.strip()
    if country in MENU_BTNS:
        # safeguard — if user taps menu, main handler already caught, but keep safe
        reset_ctx(m.from_user.id)
        return
    CTX[m.from_user.id] = {"step": "gender", "country": country}
    await m.answer(f"✅ Country selected: {country.title()}\n\nPlease select a gender:", reply_markup=GENDER_MENU)

@dp.message(lambda msg: CTX.get(msg.from_user.id, {}).get("step") == "gender")
async def step_gender(m: types.Message):
    g = m.text.strip().lower()
    if g not in ["male", "female", "mixed"]:
        if m.text in MENU_BTNS:
            reset_ctx(m.from_user.id)  # main menu buttons will be handled by top handler next time
            return
        await m.answer("❌ Please choose: Male / Female / Mixed", reply_markup=GENDER_MENU)
        return

    CTX[m.from_user.id]["gender"] = g
    CTX[m.from_user.id]["step"] = "count"
    await m.answer(
        f"✅ Gender selected: {g.title()}\n\n📊 How many names do you want?\n💡 Suggested: 10–50\n📈 Maximum: 5000\n\nPlease enter a number:"
    )

@dp.message(lambda msg: CTX.get(msg.from_user.id, {}).get("step") == "count")
async def step_count(m: types.Message):
    uid = m.from_user.id
    if not m.text.isdigit():
        # If user presses any main button during count, cancel flow gracefully
        if m.text in MENU_BTNS:
            reset_ctx(uid)
            await m.answer("🏠 Main Menu:\nSelect an option 👇", reply_markup=main_menu)
            return
        await m.answer("❌ Please enter a valid number.")
        return

    count = int(m.text)
    if count < 1 or count > 5000:
        await m.answer("❌ Enter between 1 and 5000.")
        return

    country = CTX[uid]["country"]
    gender  = CTX[uid]["gender"]

    first_list, last_list = load_first_last(country, gender)
    if not first_list or not last_list:
        reset_ctx(uid)
        await m.answer(f"❌ No name data found for {country.title()} ({gender}).\n"
                       f"📁 Expected files under <code>{NAMES_DIR}/</code> (any one scheme):\n"
                       f"• <code>{country.lower()}_{gender}_first.txt</code> + <code>{country.lower()}_{gender}_last.txt</code>\n"
                       f"• <code>{country.lower()}_{gender}.txt</code> + <code>{country.lower()}_surnames.txt</code>\n"
                       f"• <code>{country.lower()}_first.txt</code> + <code>{country.lower()}_last.txt</code>",
                       reply_markup=main_menu)
        return

    names = combo(first_list, last_list, count)

    if count <= 200:
        await m.answer(
            f"🎉 SUCCESS!\n✅ Generated {count} {gender.title()} names from {country.title()}:\n\n<code>"
            + "\n".join(names) + "</code>"
        )
    else:
        fname = f"{country.lower()}_{gender}_names.txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write("\n".join(names))
        await m.answer_document(open(fname, "rb"),
                                caption=f"✅ Generated {count} {gender.title()} names from {country.title()} saved as file.")
        os.remove(fname)

    reset_ctx(uid)

# ----------------- RUN -----------------
async def main():
    print("🚀 DataVers TG Bot is running...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
