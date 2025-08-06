from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import BOT_TOKEN, CHANNEL_ID
from db import init_db, save_ride
import logging

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Клавіатура вибору ролі
start_kb = ReplyKeyboardMarkup(resize_keyboard=True)
start_kb.add(KeyboardButton("🚗 Я водій"), KeyboardButton("🧍 Я пасажир"))

# Команда /start
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.answer("Привіт! Обери свою роль:", reply_markup=start_kb)

# Водій — початок
@dp.message_handler(lambda msg: msg.text == "🚗 Я водій")
async def driver_flow(message: types.Message):
    await message.answer("Вкажи пункт відправлення:")
    dp.register_message_handler(get_departure, state=None)

# 1. Місце відправлення
async def get_departure(message: types.Message):
    dep = message.text
    await message.answer("Куди їдемо?")
    dp.register_message_handler(lambda m: get_destination(m, dep), state=None)

# 2. Місце призначення
async def get_destination(message: types.Message, dep):
    dest = message.text
    await message.answer("Дата та час (наприклад 07.08.2025 10:00):")
    dp.register_message_handler(lambda m: get_datetime(m, dep, dest), state=None)

# 3. Дата/час
async def get_datetime(message: types.Message, dep, dest):
    dt = message.text
    await message.answer("Скільки місць?")
    dp.register_message_handler(lambda m: get_seats(m, dep, dest, dt), state=None)

# 4. Кількість місць та публікація
async def get_seats(message: types.Message, dep, dest, dt):
    seats = message.text
    username = message.from_user.username or "Немає"
    ride = {
        "user_id": message.from_user.id,
        "username": username,
        "departure": dep,
        "destination": dest,
        "datetime": dt,
        "seats": seats
    }

    save_ride(ride)

    text = (f"🚗 Поїздка водія @{username}:\n"
            f"📍 Звідки: {dep}\n"
            f"📍 Куди: {dest}\n"
            f"🕒 Коли: {dt}\n"
            f"👥 Місць: {seats}")

    await bot.send_message(CHANNEL_ID, text)
    await message.answer("✅ Опубліковано! Дякую.")

if __name__ == "__main__":
    init_db()
    executor.start_polling(dp, skip_updates=True)
