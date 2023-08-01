# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import magic_filter

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, \
    InlineKeyboardButton, InlineKeyboardMarkup, inline_keyboard_markup, \
    callback_query, CallbackQuery, ContentType
from aiogram import F

from bot_token import TOKEN
from data import STAVKI, RANGES
import my_funcs

bot = Bot(token=TOKEN)
dp = Dispatcher()

button_start: KeyboardButton = KeyboardButton(text="/start")
button_help: KeyboardButton = KeyboardButton(text="/help")
kb1: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[[button_start, button_help]], resize_keyboard=True)

b_less_3 = InlineKeyboardButton(text='меньше 3', callback_data='2')
b_3_to_5 = InlineKeyboardButton(text='от 3 до 5', callback_data='4')
b_over_5 = InlineKeyboardButton(text='5 и более', callback_data='6')
b_cancel = InlineKeyboardButton(text="Сброс", callback_data='cancel')
inline_kb = InlineKeyboardMarkup(inline_keyboard=[[b_less_3, b_3_to_5, b_over_5],[b_cancel]])

users_data = {}


@dp.message(lambda x: x.from_user.id not in users_data)
async def check_is_it_new_user(message: Message):
    my_funcs.add_user(users_data, message)
    users_data[message.from_user.id]['status'] = set()
    await message.answer(
        text='Йоу!!!\nЯ могу посчитать пошлину на авто!\nУкажите возраст а/м и\nВведите объем двигателя',
        reply_markup=inline_kb)


@dp.callback_query(F.data.in_(['2', '4', '6']))
async def year_chosen(callback: callback_query):
    print(f"'{callback.data}' inline button pressed")
    users_data[callback.from_user.id]['y'] = callback.data
    users_data[callback.from_user.id]['status'] = 'w8 vol'
    # await callback.message.edit_text(
    #     text=f'Была нажата БОЛЬШАЯ КНОПКА {callback.data}',
    #     reply_markup=callback.message.reply_markup)
    print(users_data)
    await callback.answer()


@dp.message(lambda x: x.text.isdigit() and
            users_data[x.from_user.id]['status'] == 'w8 vol')
async def get_volume(message: Message):
    u_id = message.from_user.id
    v = users_data[message.from_user.id]['volume'] = int(message.text)
    if users_data[u_id]['y'] in "46":
        stavka = STAVKI[users_data[u_id]['y']][sum(map(lambda x: v <= x, RANGES))]
        euro = round(v * stavka, 2)
        rub = round(euro * my_funcs.get_exchange_rate())
        users_data[u_id]['status'] = 'ready'
        if rub:
            await message.reply(text=f"Пошлина составит {euro} €\nчто по текущему курсу {rub} ₽")
        else:
            await message.reply(text=f"Пошлина составит {euro} €\nне удалось получить курс €\nдля расчета в ₽")
        # await message.answer(text='Укажите возраст авто', reply_markup=inline_kb)



@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    await message.answer(
        text='''Привет!
        Я могу посчитать пошлину на авто!
        Укажите возраст а/м и
        Введите объем двигателя''',
        reply_markup=inline_kb)


@dp.message(Command(commands=["help"]))
async def process_start_command(message: Message):
    await message.answer('Пока могу посчитать только для а/м с ДВС от 3 лет', reply_markup=kb1)

"""
@dp.message(F.text)
async def calculate(message: Message):
    try:
        v = int(message.text)
        stavka = STAVKI['4'][sum(map(lambda x: v <= x, RANGES))]
        euro = round(v * stavka, 2)
        rub = round(euro * my_funcs.get_exchange_rate())
        if rub:
            pass
            # await message.reply(text=f"Пошлина составит {euro} €\nчто по текущему курсу {rub} ₽")
        else:
            pass
            # await message.reply(text=f"Пошлина составит {euro} €\nне удалось получить курс €\nдля расчета в ₽")
        await message.answer(text='Укажите возраст авто', reply_markup=inline_kb)
    except ValueError:
        await message.reply("Введите число")
"""

@dp.message(F.text)
async def send_echo(message: Message):
    await message.reply(text=message.text)


@dp.message(F.content_type == ContentType.VOICE)
async def send_echo(message: Message):
    await message.reply(text='войсоледи')


if __name__ == '__main__':
    dp.run_polling(bot)
