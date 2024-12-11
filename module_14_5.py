from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from crud_functions import *
import asyncio

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton(text='Рассчитать норму калорий')
button2 = KeyboardButton(text='Формулы расчёта')
button3 = KeyboardButton(text='Купить')
button4 = KeyboardButton(text='Регистрация')
kb.add(button1, button2)
kb.add(button3, button4)

data = get_all_products()

inline_kb = InlineKeyboardMarkup(resize_keyboard=True)
for i in range(1, 5):
    inline_kb.insert(InlineKeyboardButton(text=f'Продукт{i}', callback_data='product_buying'))


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = 1000


@dp.message_handler(commands='start')
async def start(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)


@dp.message_handler(text='Купить')
async def get_buying_list(message):
    for i in range(1, 5):
        with open(f'pics/{i}.jpg', 'rb') as img:
            await message.answer_photo(img,
                                       f'Название: {data[i - 1][1]} | Описание: {data[i - 1][2]} | Цена: {data[i - 1][3]} ')
    await message.answer('Выберите продукт для покупки:', reply_markup=inline_kb)
    #await message.answer


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')


@dp.message_handler(text='Формулы расчёта')
async def get_formulas(message):
    await message.answer('10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5')


@dp.message_handler(text='Рассчитать норму калорий')
async def set_age(message):
    await message.answer('Введите свой возраст:')
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    if not message.text.isdigit() or int(message.text) == 0:
        await message.answer('Введите положительное целое число!')
        return None
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост, см:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    if not message.text.isdigit() or int(message.text) == 0:
        await message.answer('Введите положительное целое число!')
        return None
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес, кг:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def set_calories(message, state):
    if not message.text.isdigit() or int(message.text) == 0:
        await message.answer('Введите положительное целое число!')
        return None
    await state.update_data(weight=message.text)
    data = await state.get_data()
    calories = int(data['growth']) * 6.25 + int(data['weight']) * 10 - int(data['age']) * 5 + 5
    await message.answer(f'Ваша калорийность равна {calories} кал')
    await state.finish()


@dp.message_handler(text='Регистрация')
async def sign_up(message):
    await message.answer('Введите имя пользователя (только латинский алфавит):')
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    if not is_included(message.text):
        await state.update_data(username=message.text)
        await message.answer('Введите email:')
        await RegistrationState.email.set()
    else:
        await message.answer('Пользователь существует, введите другое имя')
        await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email=message.text)
    await message.answer('Введите возраст:')
    await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(age=message.text)
    data = await state.get_data()
    add_user(data['username'], data['email'], int(data['age']))
    await state.finish()
    await message.answer('Регистрация прошла успешно!')


@dp.message_handler()
async def all_message(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
