import asyncio
import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import CallbackQuery, Message

# --- НАСТРОЙКА ЛОГИРОВАНИЯ ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Загружаем переменные из .env
load_dotenv()

# --- НАСТРОЙКИ ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("❌ Критическая ошибка: Не найден BOT_TOKEN в файле .env!")
    raise RuntimeError("Создай файл .env и добавь туда BOT_TOKEN=твой_новый_токен")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- ДАННЫЕ КВИЗА ---
QUIZ_DATA = [
    {
        "question": "🌊 Вопрос 1. Этот ёкай живёт в воде, обожает огурцы 🥒 и может утопить человека, если тот забудет про главное правило вежливости. Кто это?",
        "options": ["Тэнгу", "Каппа", "Дзасики-вараси", "Юки-онна"],
        "correct_index": 1,
        "explanation": "💧 Каппа — речной ёкай. Ему приносят в дар огурцы 🥒. А чтобы спастись от него, нужно поклониться: он рефлекторно поклонится в ответ и прольёт воду из углубления на голове — и сразу потеряет силу! 🙇‍♂️"
    },
    {
        "question": "🏠 Вопрос 2. В доме иногда слышен тихий смех, а на полу остаются маленькие следы. Говорят, это озорной дух-ребёнок, который приносит удачу дому, пока живёт в нём. Как его зовут?",
        "options": ["Дзасики-вараси", "Каппа", "Рокурокуби", "Нурарихён"],
        "correct_index": 0,
        "explanation": "🧸 Дзасики-вараси — домашний дух в образе ребёнка. Если он уходит, дом теряет удачу. Похож на славянского домового, но с японским характером! 🎌"
    },
    {
        "question": "🌑 Вопрос 3. По легенде, этот ёкай выглядит как обычный кусок ткани, который катится по дороге ночью. Но стоит подойти ближе — и он оборачивается, а у него вдруг появляется лицо с огромными глазами 👀 и длинным языком 👅. Что это за существо?",
        "options": ["Тётин-юрей", "Убумэ", "Иттан-момэн", "Аканамэ"],
        "correct_index": 2,
        "explanation": "👻 Иттан-момэн — это «кусок полотна», который оживает ночью. В старых японских рассказах он пугает путников: выглядит безобидно, а потом резко оборачивается и показывает жуткое лицо! 😱"
    },
    {
        "question": "🌙 Вопрос 4. У этого существа может удлиняться шея, а голова будто «отделяется» и летает по комнате. Чаще всего это женский образ, пугающий людей по ночам. Кто это?",
        "options": ["Юки-онна", "Обаке", "Мононокэ", "Рокурокуби"],
        "correct_index": 3,
        "explanation": "🗣️ Рокурокуби — один из самых узнаваемых «ночных» ёкаев: днём это обычная женщина, а ночью её шея удлиняется или голова отделяется. Жуть! 😨"
    },
    {
        "question": "🦊 Вопрос 5. Это существо с лисьими ушами и несколькими хвостами может принимать облик красивой женщины, чтобы обманывать людей. Оно любит розыгрыши, но иногда бывает и по-настоящему опасным. Кто это?",
        "options": ["Тэнгу", "Кицунэ", "Нурарихён", "Юрей"],
        "correct_index": 1,
        "explanation": "🦊 Кицунэ — лиса-оборотень, один из самых известных ёкаев в поп‑культуре. Чем больше у неё хвостов, тем она старше и сильнее. Может быть и озорной, и мстительной! 😈"
    }
]

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def get_keyboard(options, question_index, current_score):
    builder = InlineKeyboardBuilder()
    for i, opt in enumerate(options):
        callback_data = f"quiz_{question_index}_{i}_{current_score}"
        builder.button(text=opt, callback_data=callback_data)
    
    builder.adjust(1)  # Кнопки друг под другом
    return builder.as_markup()

def get_final_text_and_keyboard(score):
    total = len(QUIZ_DATA)
    percent = (score / total) * 100

    if percent == 100:
        advice = "🎉 Ты настоящий эксперт по ёкаям! 🎌"
    elif percent >= 60:
        advice = "👍 Хороший уровень! Тебе точно понравятся аниме про ёкаев, например «Внук Нурарихёна» или «Щелкунчик Китаро». 📺"
    else:
        advice = "🤔 Не беда! Это отличный повод познакомиться с японской мифологией. Начни с «Щелкунчик Китаро» — он как энциклопедия ёкаев! 📚"

    text = (
        f"📜 Квиз завершён! Ты ответил правильно на {score}/{total} вопросов ({percent:.0f}%).\n\n"
        f"{advice}"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="🔁 Начать заново", callback_data="restart_quiz")
    builder.adjust(1)
    
    return text, builder.as_markup()

# --- ХЕНДЛЕРЫ ---
@dp.message(Command("start"))
async def cmd_start(message: Message):
    logger.info(f"Пользователь {message.from_user.id} нажал /start")
    await message.answer(
        "👋 Привет! Я бот-квиз про ёкаев. Готов проверить, насколько ты знаешь японский фольклор? 🎌\n"
        "Нажми /quiz, чтобы начать, или /restart, чтобы сбросить прогресс. 🔥"
    )

@dp.message(Command("quiz"))
async def start_quiz(message: Message):
    logger.info(f"Пользователь {message.from_user.id} начал квиз")
    q = QUIZ_DATA[0]
    kb = get_keyboard(q["options"], 0, 0)
    await message.answer(text=q["question"], reply_markup=kb)

@dp.message(Command("restart"))
async def restart_quiz_command(message: Message):
    """Принудительный перезапуск квиза через команду"""
    logger.info(f"Пользователь {message.from_user.id} перезапустил квиз через /restart")
    q = QUIZ_DATA[0]
    kb = get_keyboard(q["options"], 0, 0)
    # ИСПРАВЛЕНИЕ: отправляем вопрос + кнопки, а не просто сообщение
    await message.answer(text=q["question"], reply_markup=kb)

@dp.callback_query(F.data == "restart_quiz")
async def restart_quiz_button(callback: CallbackQuery):
    """Перезапуск квиза по кнопке «Начать заново»"""
    logger.info(f"Пользователь {callback.from_user.id} перезапустил квиз по кнопке")
    q = QUIZ_DATA[0]
    kb = get_keyboard(q["options"], 0, 0)
    try:
        await callback.message.edit_text(
            text=q["question"],
            reply_markup=kb
        )
    except Exception:
        # Если нельзя отредактировать — отправляем новое сообщение с вопросом
        await callback.message.answer(text=q["question"], reply_markup=kb)

@dp.callback_query(F.data.startswith("quiz_"))
async def process_quiz_answer(callback: CallbackQuery):
    data = callback.data
    logger.debug(f"Получен callback: {data}")
    
    parts = data.split("_")
    
    if len(parts) < 4:
        logger.warning(f"Некорректные данные callback от пользователя {callback.from_user.id}: {data}")
        await callback.answer("❌ Ошибка данных. Пожалуйста, начните квиз заново командой /quiz.", show_alert=True)
        return

    try:
        question_index = int(parts[1])
        chosen_index = int(parts[2])
        score_before = int(parts[3])
    except ValueError:
        logger.error(f"Ошибка преобразования данных в числа: {data}")
        await callback.answer("❌ Некорректные данные ответа. Начните квиз заново.", show_alert=True)
        return

    if not (0 <= question_index < len(QUIZ_DATA)):
        logger.warning(f"Индекс вопроса вне диапазона: {question_index}")
        await callback.answer("❌ Вопрос не найден. Начните квиз заново.", show_alert=True)
        return

    q = QUIZ_DATA[question_index]

    if not (0 <= chosen_index < len(q["options"])):
        logger.warning(f"Индекс ответа вне диапазона для вопроса {question_index}: {chosen_index}")
        await callback.answer("❌ Неверный вариант ответа. Начните квиз заново.", show_alert=True)
        return

    is_correct = (chosen_index == q["correct_index"])
    new_score = score_before + (1 if is_correct else 0)

    correct_text = q["options"][q["correct_index"]]
    feedback = "✅ Верно!" if is_correct else f"❌ Неверно. Правильный ответ: {correct_text}"

    try:
        await callback.message.edit_text(
            text=f"{feedback}\n\n📜 Пояснение: {q['explanation']}"
        )
    except Exception as e:
        logger.error(f"Не удалось отредактировать сообщение: {e}")
        await callback.message.answer(f"{feedback}\n\n📜 Пояснение: {q['explanation']}")

    await asyncio.sleep(3)
    next_index = question_index + 1

    if next_index >= len(QUIZ_DATA):
        final_text, kb = get_final_text_and_keyboard(new_score)
        await callback.message.answer(final_text, reply_markup=kb)
    else:
        q_next = QUIZ_DATA[next_index]
        kb = get_keyboard(q_next["options"], next_index, new_score)
        await callback.message.answer(text=q_next["question"], reply_markup=kb)

# --- ГЛАВНАЯ ФУНКЦИЯ ---
async def main():
    logger.info("🗑️ Удаляем старые вебхуки (на всякий случай)...")
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("✅ Вебхуки удалены. Запускаем polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем.")
    except Exception as e:
        logger.critical(f"💥 Критическая ошибка при запуске: {e}")
