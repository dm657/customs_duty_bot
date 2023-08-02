# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import magic_filter

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, \
    InlineKeyboardButton, InlineKeyboardMarkup, \
    callback_query, CallbackQuery, ContentType
from aiogram import F
# from aiogram.methods import edit_message_text

from bot_token import TOKEN
from data import STAVKI, RANGES, INIT_MSG, RES_SAMPLE_RU
import my_funcs

bot = Bot(token=TOKEN)
dp = Dispatcher()

button_go: KeyboardButton = KeyboardButton(text="/начать")
button_reset_start: KeyboardButton = KeyboardButton(text="/сброс")
kb1: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[[button_go, button_reset_start]],
    resize_keyboard=True, one_time_keyboard=False)

b_less_3 = InlineKeyboardButton(text='меньше 3', callback_data=',менее 3')
b_3_to_5 = InlineKeyboardButton(text='от 3 до 5', callback_data='от 3 до 5')
b_over_5 = InlineKeyboardButton(text='5 и более', callback_data='старше 5')
b_done = InlineKeyboardButton(text="готово", callback_data='next')
b_cancel = InlineKeyboardButton(text="Сброс", callback_data='cancel')

years_kb = InlineKeyboardMarkup(inline_keyboard=[[b_less_3, b_3_to_5, b_over_5]])
two_line_kb = InlineKeyboardMarkup(inline_keyboard=[[b_less_3, b_3_to_5, b_over_5], [b_cancel]])
two_line_with_done_kb = InlineKeyboardMarkup(inline_keyboard=[[b_less_3, b_3_to_5, b_over_5], [b_done, b_cancel]])

users_data = {}


@dp.message(Command(commands=["start", "сброс"]))
async def process_start_command(message: Message):
    await message.delete()
    await message.answer(
        text='''Привет!
Я могу посчитать пошлину на авто!''',
        reply_markup=kb1)
    await message.answer(text=INIT_MSG, reply_markup=years_kb)
    my_funcs.add_user(users_data, message)
    users_data[message.from_user.id]['msg_id'] = message.message_id + 2
    users_data[message.from_user.id]['status'] = 'w8_year'


@dp.message(Command(commands=['/начать']))
async def starting(message: Message):
    print(message.message_id)
    await message.delete()
    await message.answer(
        text=INIT_MSG,
        reply_markup=years_kb)
    my_funcs.add_user(users_data, message)
    users_data[message.from_user.id]['status'] = 'w8_year'
    users_data[message.from_user.id]['msg_id'] = message.message_id + 1


# @dp.message(lambda x: users_data[x.from_user.id].get('status') == 'done')
#                       # x.from_user.id not in users_data)
# async def going_on(message: Message):
#     # print()
#     # my_funcs.add_user(users_data, message)
#     # users_data[message.from_user.id]['status'] = 'w8_year'
#     await message.delete()


@dp.callback_query(F.data.in_(['менее 3', 'от 3 до 5', 'старше 5']))
async def year_chosen(callback: callback_query):
    print(f"'{callback.data}' inline button pressed")
    users_data[callback.from_user.id]['y'] = callback.data
    users_data[callback.from_user.id]['status'] = 'w8 vol'
    print(callback.message.message_id)
    await callback.answer('got it!')


@dp.message(lambda x: x.text.isdigit() and
            users_data[x.from_user.id]['status'] == 'w8 vol')
async def get_volume(message: Message):
    u_id = message.from_user.id
    v = users_data[message.from_user.id]['volume'] = int(message.text)
    if users_data[u_id]['y'] in ['от 3 до 5', 'старше 5']:
        stavka = STAVKI[users_data[u_id]['y']][sum(map(lambda x: v <= x, RANGES))]
        euro = round(v * stavka, 2)
        eur_ex_rate = my_funcs.get_exchange_rate()
        rub = f"{round(euro * eur_ex_rate):_}".replace('_', ' ')
        users_data[u_id]['status'] = 'done'
        if rub:  # rub == 0 if unable to get exchange rate
            await message.delete()
            users_data[u_id]['last_result'] = RES_SAMPLE_RU.format(
                users_data[u_id]['y'], v, euro, eur_ex_rate, rub)

            await bot.edit_message_text(
                text=RES_SAMPLE_RU.format(users_data[u_id]['y'], v, euro, eur_ex_rate, rub),
                reply_markup=two_line_with_done_kb, chat_id=message.chat.id,
                message_id=users_data[u_id]['msg_id'])
        else:
            await message.reply(text=f"Пошлина составит {euro} €\nне удалось получить курс €\nдля расчета в ₽")
        # await message.answer(text='Укажите возраст авто', reply_markup=inline_kb)


@dp.callback_query(F.data == 'cancel')
async def press_cancel(callback: callback_query):
    users_data[callback.from_user.id]['status'] = 'w8 vol'
    await callback.message.edit_text(text=INIT_MSG, reply_markup=years_kb)


@dp.callback_query(F.data == 'next')
async def press_next(callback: callback_query):
    users_data[callback.from_user.id]['status'] = 'w8_year'
    await callback.message.edit_text(
        text=f"{users_data[callback.from_user.id]['last_result']} ", reply_markup=None)
    my_funcs.add_user(users_data, callback)
    users_data[callback.from_user.id]['msg_id'] = callback.message.message_id + 2
    print(callback.message.message_id)
    await callback.message.answer(text=INIT_MSG, reply_markup=years_kb)


@dp.message(Command(commands=["help"]))
async def process_start_command(message: Message):
    pass
    # await message.answer('Пока могу посчитать только для а/м с ДВС от 3 лет', reply_markup=kb1)


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
    await message.delete()


@dp.message()
async def send_echo(message: Message):
    await message.delete()


@dp.message(F.content_type == ContentType.VOICE)
async def send_echo(message: Message):
    await message.reply(text="голосовое своё себе отправь")


if __name__ == '__main__':
    dp.run_polling(bot)
