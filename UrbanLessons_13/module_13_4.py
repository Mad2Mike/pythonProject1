from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = ''

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()
    gender = State()


@dp.message_handler(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Введите 'Calories' для начала расчета нормы калорий.")


@dp.message_handler(lambda message: message.text == "Calories")
async def set_gender(message: types.Message):
    await message.answer("Введите ваш пол (мужчина/женщина):")
    await UserState.gender.set()


@dp.message_handler(state=UserState.gender)
async def set_age(message: types.Message, state: FSMContext):
    gender = message.text.lower()
    if gender in ["мужчина", "женщина"]:
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


@dp.message_handler(lambda message: message.text.lower() != "calories", state="*")
async def handle_invalid_input(message: types.Message):
    await message.answer("Пожалуйста, введите команду /start для начала или 'Calories' для расчета нормы калорий.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
