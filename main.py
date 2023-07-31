# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import magic_filter

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command #, Text

from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, inline_keyboard_markup
from aiogram import F

from bot_token import TOKEN
from data import STAVKI, RANGES
from get_exchange_rate import get_exchange_rate

bot = Bot(token=TOKEN)
dp = Dispatcher()

button_start: KeyboardButton = KeyboardButton(text="/start")
button_help: KeyboardButton = KeyboardButton(text="/help")
kb1: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[[button_start, button_help]], resize_keyboard=True)

# button_1: KeyboardButton = KeyboardButton(text='кинуть 🎲')
# button_2: KeyboardButton = KeyboardButton(text='Собакены')
#
# # Создаем объект клавиатуры, добавляя в него кнопки
# kb1: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
#     keyboard=[[button_1, button_2]], resize_keyboard=True)


@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    await message.answer('Привет!\nЯ могу посчитать пошлину на авто!\nНапиши объем двигателя машины', reply_markup=kb1)


@dp.message(Command(commands=["help"]))
async def process_start_command(message: Message):
    await message.answer('Пока могу посчитать только для а/м с ДВС от 3 до 5 лет', reply_markup=kb1)


@dp.message(F.voice)
async def send_echo(message: Message):
    await message.reply(text='войсоледи')


# @dp.message(lambda x: x.text and '123' in x.text or (x.text and x.text.isdigit() and 1 <= int(x.text) <= 100))
@dp.message(F.text)
async def calculate(message: Message):
    try:
        v = int(message.text)
        stavka = STAVKI[sum(map(lambda x: v <= x, RANGES))]
        euro = round(v * stavka, 2)
        rub = round(euro * get_exchange_rate())
        if rub:
            await message.reply(text=f"Пошлина составит {euro} €\nчто по текущему курсу {rub} ₽")
        else:
            await message.reply(text=f"Пошлина составит {euro} €\nне удалось получить курс €\nдля расчета в ₽")
    except ValueError:
        await message.reply("Введите число")


@dp.message(F.text)
async def send_echo(message: Message):
    await message.reply(text=message.text)


if __name__ == '__main__':
    dp.run_polling(bot)
