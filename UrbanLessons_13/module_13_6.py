from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = ''

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

inline_kb = InlineKeyboardMarkup()
button_calories = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button_formulas = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
inline_kb.add(button_calories, button_formulas)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()
    gender = State()


@dp.message_handler(Command("start"))
async def cmd_start(message: types.Message):
    kb = InlineKeyboardMarkup(resize_keyboard=True)
    button = InlineKeyboardButton(text='Рассчитать', callback_data='calculate')
    button_info = InlineKeyboardButton(text='Информация', callback_data='info')
    kb.add(button, button_info)
    await message.answer("Выберите опцию:", reply_markup=kb)


@dp.callback_query_handler(lambda call: call.data == 'calculate')
async def main_menu(call: types.CallbackQuery):
    await call.message.answer("Выберите опцию:", reply_markup=inline_kb)


@dp.callback_query_handler(lambda call: call.data == 'formulas')
async def get_formulas(call: types.CallbackQuery):
    formula_message = "Формула Миффлина-Сан Жеора:\n\n" \
                      "Для мужчин: BMR = 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (годы) + 5\n" \
                      "Для женщин: BMR = 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (годы) - 161"
    await call.message.answer(formula_message)


@dp.callback_query_handler(lambda call: call.data == 'calories')
async def choose_gender(call: types.CallbackQuery):
    # Создаем инлайн-клавиатуру для выбора гендера
    gender_kb = InlineKeyboardMarkup()
    button_male = InlineKeyboardButton(text='Мужчина', callback_data='gender_male')
    button_female = InlineKeyboardButton(text='Женщина', callback_data='gender_female')
    gender_kb.add(button_male, button_female)

    await call.message.answer("Пожалуйста, выберите ваш пол:", reply_markup=gender_kb)
    await UserState.gender.set()

@dp.callback_query_handler(lambda call: call.data in ['gender_male', 'gender_female'], state=UserState.gender)
async def set_gender(call: types.CallbackQuery, state: FSMContext):
    gender = 'мужчина' if call.data == 'gender_male' else 'женщина'
    await state.update_data(gender=gender)
    await call.message.answer("Введите свой возраст:")
    await UserState.age.set()

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
    await message.answer("Пожалуйста, введите команду /start для начала или 'Рассчитать' для расчета нормы калорий.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)