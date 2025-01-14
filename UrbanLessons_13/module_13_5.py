from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = '8119644202:AAFUc5SejgENU7q1R3rf50jms8XNRj4FArQ'

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton(text='Расчитать')
button2 = KeyboardButton(text='Информация')

kb.add(button)
kb.add(button2)



class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()
    gender = State()


@dp.message_handler(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Введите 'Расчитать' для начала расчета нормы калорий.", reply_markup=kb)


@dp.message_handler(lambda message: message.text == "Расчитать")
async def set_gender(message: types.Message):
    await message.answer("Введите ваш пол (мужчина/женщина):")
    await UserState.gender.set()



@dp.message_handler(state=UserState.gender)
async def set_age(message: types.Message, state: FSMContext):
    gender = message.text.lower()
    if gender in ["Мужчина", "Женщина"]:
        await state.update_data(gender=gender)
        await message.answer("Введите свой возраст:")
        await UserState.age.set()
    else:
        await message.answer("Пожалуйста, введите 'мужчина' или 'женщина'.")


@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Введите свой рост:")
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=message.text)
    await message.answer("Введите свой вес:")
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)
    data = await state.get_data()

    age = int(data.get('age'))
    growth = int(data.get('growth'))
    weight = int(data.get('weight'))
    gender = data.get('gender')

    if gender == "мужчина":
        bmr = 10 * weight + 6.25 * growth - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * growth - 5 * age - 161

    await message.answer(f"Ваша норма калорий: {bmr} ккал.")
    await state.finish()


@dp.message_handler(lambda message: message.text.lower() != "расчитать", state="*")
async def handle_invalid_input(message: types.Message):
    await message.answer("Пожалуйста, введите команду /start для начала или 'Расчитать' для расчета нормы калорий.")

@dp.message_handler(state="*")
async def debug_state(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    await message.answer(f"Текущее состояние: {current_state}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
