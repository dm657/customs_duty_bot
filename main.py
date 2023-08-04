# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from pytz import timezone
# from datetime import datetime as dt

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, \
    InlineKeyboardButton, InlineKeyboardMarkup, \
    callback_query, CallbackQuery, ContentType
from aiogram import F
# from aiogram.methods import edit_message_text

from bot_token import TOKEN
from data import STAVKI, RANGES, INIT_MSG, RES_SAMPLE_RU, EXCHANGE_RATE_SAMPLE, T_ZONE
import my_funcs

bot = Bot(token=TOKEN)
dp = Dispatcher()

button_go: KeyboardButton = KeyboardButton(text="/начать")
button_reset_start: KeyboardButton = KeyboardButton(text="/сброс")
kb1: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[[button_go, button_reset_start]],
    resize_keyboard=True, one_time_keyboard=False)
# ֍֎
b_less_3 = InlineKeyboardButton(text='меньше 3', callback_data=',менее 3')
b_3_to_5 = InlineKeyboardButton(text='от 3 до 5', callback_data='от 3 до 5')
b_over_5 = InlineKeyboardButton(text='5 и более', callback_data='старше 5')
b_done = InlineKeyboardButton(text="готово", callback_data='next')
b_blank = InlineKeyboardButton(text=' ', callback_data='do_nothing')
b_cancel = InlineKeyboardButton(text="Сброс", callback_data='cancel')

years_kb = InlineKeyboardMarkup(inline_keyboard=[[b_less_3, b_3_to_5, b_over_5]])
blank_cancel_kb = InlineKeyboardMarkup(inline_keyboard=[[b_blank, b_cancel]])
done_cancel_kb = InlineKeyboardMarkup(inline_keyboard=[[b_done, b_cancel]])
# two_line_with_done_kb = InlineKeyboardMarkup(
#     inline_keyboard=[[b_less_3, b_3_to_5, b_over_5], [b_done, b_cancel]])

users_data = {}
exchange_rates = EXCHANGE_RATE_SAMPLE


@dp.message(lambda x: x.from_user.id not in users_data)
@dp.message(Command(commands=["start", "сброс"]))
async def process_start_command(message: Message):
    await message.delete()
    await message.answer(
        text='''Привет!
Я могу посчитать пошлину на авто!''',
        reply_markup=kb1)
    await message.answer(text=INIT_MSG, reply_markup=years_kb)
    my_funcs.add_user(users_data, message)
    # users_data[message.from_user.id]['msg_id'] = message.message_id + 2
    users_data[message.from_user.id]['status'] = 'w8_year'
    # print('saved msg_id', users_data[message.from_user.id]['msg_id'])


@dp.message(Command(commands=['/начать']))
async def starting(message: Message):
    print(message.message_id)
    await message.delete()
    await message.answer(
        text=INIT_MSG,
        reply_markup=years_kb)
    my_funcs.add_user(users_data, message)
    users_data[message.from_user.id]['status'] = 'w8_year'


@dp.callback_query(F.data.in_(['менее 3', 'от 3 до 5', 'старше 5']))
async def year_chosen(callback: callback_query):
    # print(callback.model_dump_json())
    users_data[callback.from_user.id]['y'] = callback.data
    users_data[callback.from_user.id]['status'] = 'w8_vol'
    users_data[callback.from_user.id]['msg_id'] = callback.message.message_id
    print(f"year chosen. message.callback.id {callback.message.message_id}")
    await callback.answer('got it!')
    await bot.edit_message_text(text='Принято! Следующй шаг:\nВведите объем двигателя в См³',
                                reply_markup=blank_cancel_kb,
                                chat_id=callback.message.chat.id, message_id=callback.message.message_id)


@dp.message(lambda x: (x.text and x.text.isdigit()
                       and users_data[x.from_user.id]['status'] == 'w8_vol'))
async def get_volume(message: Message):
    print(f"vol entered. message.message_id {message.message_id}")
    u_id = message.from_user.id
    v = users_data[message.from_user.id]['volume'] = int(message.text)
    if users_data[u_id]['y'] in ['от 3 до 5', 'старше 5']:
        stavka = STAVKI[users_data[u_id]['y']][sum(map(lambda x: v <= x, RANGES))]
        euro = round(v * stavka, 2)
        eur_ex_rate = my_funcs.get_exchange_rate(exchange_rates)
        rub = f"{round(euro * eur_ex_rate):_}".replace('_', ' ')
        users_data[u_id]['status'] = 'done'
        if eur_ex_rate:  # eur_ex_rate == 0 if unable to get exchange rate
            await message.delete()
            users_data[u_id]['last_result'] = RES_SAMPLE_RU.format(
                users_data[u_id]['y'], v, euro, eur_ex_rate, rub)

            await bot.edit_message_text(
                text=RES_SAMPLE_RU.format(users_data[u_id]['y'], v, euro, eur_ex_rate, rub),
                reply_markup=done_cancel_kb, chat_id=message.chat.id, message_id=users_data[u_id]['msg_id'])
        else:
            await message.reply(text=f"Пошлина составит {euro} €\nне удалось получить курс €\nдля расчета в ₽")


@dp.callback_query(F.data == 'cancel')
async def press_cancel(callback: callback_query):
    users_data[callback.from_user.id]['status'] = 'w8_year'
    await callback.message.edit_text(text=INIT_MSG, reply_markup=years_kb)


@dp.callback_query(F.data == 'next')
async def press_next(callback: callback_query):
    users_data[callback.from_user.id]['status'] = 'w8_year'
    await callback.message.edit_text(
        text=f"{users_data[callback.from_user.id]['last_result']} ", reply_markup=None)
    my_funcs.add_user(users_data, callback)
    await callback.message.answer(text=INIT_MSG, reply_markup=years_kb)


@dp.callback_query(F.data == 'do_nothing')
async def press_blank(callback: callback_query):
    await callback.answer()


@dp.message(Command(commands=["help"]))
async def process_start_command(message: Message):
    pass
    # await message.answer('Пока могу посчитать только для а/м с ДВС от 3 лет', reply_markup=kb1)


@dp.message(F.content_type == ContentType.VOICE)
async def send_echo(message: Message):
    await message.reply(text="голосовое своё себе отправь")


@dp.message()
async def send_echo(message: Message):
    await message.delete()


if __name__ == '__main__':
    dp.run_polling(bot)
