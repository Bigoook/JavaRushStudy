from enum import Enum
from telegram.ext import (
    ApplicationBuilder, CallbackQueryHandler, ContextTypes,
    CommandHandler, CallbackContext, MessageHandler, filters, ConversationHandler
)

from gpt import ChatGptService
from util import *
from credentials import config


# ====== ENUM для станів ======
class RandomState(Enum):
    RUNNING = 1

class GptState(Enum):
    RUNNING = 1

class TalkState(Enum):
    CHOOSING_PERSON = 1
    TALKING = 2

class QuizState(Enum):
    CHOOSING_QUIZ = 1
    QUIZ_RUNNING = 2

class TranslateState(Enum):
    CHOOSING_LANG = 1
    TRANSLATING = 2

class ResumeState(Enum):
    ASK_RESUME = 1

# Random
async def random(update, context):
    await show_mode_screen(update, context, "random")
    answer = await ask_gpt(chat_gpt,"random", "Згенеруй один цікавий факт прямо зараз.")
    await send_text_buttons(update, context, answer or "Не вдалося отримати факт 😔", {
        "random_end": "Закінчити",
        "random_more": "Хочу ще факт"
    })
    return RandomState.RUNNING

async def random_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()
    if query == "random_end":
        return await start(update, context)
    return await random(update, context)


# GPT
async def gpt(update, context):
    await show_mode_screen(update, context, "gpt")
    return GptState.RUNNING

async def gpt_dialog(update, context):
    text = update.message.text
    answer = await ask_gpt(chat_gpt,"gpt", text)
    await send_text(update, context, answer or "Не вдалося отримати відповідь 😔")
    return GptState.RUNNING


# Talk
async def talk(update, context):
    await show_mode_screen(update, context, "talk", {
        "talk_cobain": "Курт Кобейн",
        "talk_queen": "Королева Єлизавета",
        "talk_tolkien": "Дж.Р.Р. Толкін",
        "talk_nietzsche": "Фрідріх Ніцше",
        "talk_hawking": "Стівен Гокінг"
    })
    return TalkState.CHOOSING_PERSON

async def talk_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()
    if query == "talk_end":
        return await start(update, context)
    await show_mode_screen(update, context, query, text="Готовий відповісти на всі ваші питання!")
    context.user_data["talk_topic"] = query
    return TalkState.TALKING

async def talk_dialog(update, context):
    text = update.message.text
    topic = context.user_data.get("talk_topic", "talk_cobain")
    answer = await ask_gpt(chat_gpt,prompt_name = topic, user_text = text)
    await send_text_buttons(update, context, answer or "Нічого не скажу 😔", {
        "talk_end": "Закінчити"
    })
    return TalkState.TALKING


# Quiz
async def quiz(update, context):
    await show_mode_screen(update, context, "quiz", {
        "quiz_prog": "Програмування на Python",
        "quiz_math": "Математика",
        "quiz_biology": "Біологія"
    })
    return QuizState.CHOOSING_QUIZ

async def quiz_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()
    context.user_data["quiz_topic"] = query
    msg = await send_text(update, context, "Готую питання!")
    answer = await ask_gpt(chat_gpt, prompt_name=load_prompt("quiz"), user_text=query)
    await msg.edit_text(answer or "Не придумав питання 😔")
    return QuizState.QUIZ_RUNNING

async def quiz_dialog(update, context):
    text = update.message.text
    answer = await chat_gpt.add_message(text)
    if "Правильно!" in answer:
        context.user_data["quiz_score"] = context.user_data.get("quiz_score", 0) + 1
    score = context.user_data.get("quiz_score", 0)
    answer_with_score = f"{answer}\n\nВаш рахунок: {score}"
    await send_text_buttons(update, context, answer_with_score, {
        "quiz_more": "Ще питання",
        "quiz_change": "Змінити тему",
        "quiz_end": "Закінчити"
    })
    return QuizState.QUIZ_RUNNING

async def quiz_control(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()
    if query == "quiz_end":
        return await start(update, context)
    elif query == "quiz_change":
        return await quiz(update, context)
    elif query == "quiz_more":
        topic = context.user_data.get("quiz_topic", "quiz_prog")
        msg = await send_text(update, context, "Готую питання!")
        answer = await ask_gpt(chat_gpt, prompt_name=load_prompt("quiz"), user_text=topic)
        await msg.edit_text(answer or "Не придумав питання 😔")
    return QuizState.QUIZ_RUNNING


# Translate
async def translate(update, context):
    await show_mode_screen(update, context, "translate", {
        "lang_en": "Англійська",
        "lang_de": "Німецька",
        "lang_fr": "Французька",
        "lang_es": "Іспанська"
    }, text="Обери мову, на яку потрібно перекласти текст:")
    return TranslateState.CHOOSING_LANG

async def translate_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()
    context.user_data["translate_lang"] = query
    await send_text(update, context, "Надішліть текст для перекладу.")
    return TranslateState.TRANSLATING

async def translate_dialog(update, context):
    text = update.message.text
    lang = context.user_data.get("translate_lang", "lang_en")
    answer = await ask_gpt(chat_gpt,"translate", text, extra=f"Мова для перекладу: {lang}")
    await send_text_buttons(update, context, answer or "Не вдалося отримати переклад 😔", {
        "change_lang": "Змінити мову",
        "translate_end": "Закінчити"
    })
    return TranslateState.TRANSLATING

async def translate_control(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()
    if query == "translate_end":
        return await start(update, context)
    elif query == "change_lang":
        return await translate(update, context)
    return TranslateState.TRANSLATING

#resume
async def resume(update, context):
    await send_text(update, context,
        "Введіть одним повідомленням вашу освіту, досвід роботи та навички.\n"
        "Наприклад:\n"
        "Освіта: КНУ, комп’ютерні науки, 2015–2019\n"
        "Досвід роботи: SoftServe, Python Developer, 2019–2023\n"
        "Навички: Python, Django, SQL"
    )
    return ResumeState.ASK_RESUME

async def generate_resume(update, context):
    user_data = update.message.text
    answer = await chat_gpt.send_question(prompt_text=load_prompt("resume"), message_text=user_data)

    await send_text(update, context, answer or "Не вдалося сформувати резюме 😔")
    return ConversationHandler.END

# ====== Головне меню ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_mode_screen(update, context, "main")
    await show_main_menu(update, context, {
        'start': 'Головне меню',
        'random': 'Дізнатися випадковий цікавий факт 🧠',
        'gpt': 'Задати питання чату GPT 🤖',
        'talk': 'Поговорити з відомою особистістю 👤',
        'quiz': 'Взяти участь у квізі ❓',
        'translate': 'Перекладач 🌐',
        'resume':'Допомога з резюме 📄'
    })
    return ConversationHandler.END


# ====== Реєстрація ======
chat_gpt = ChatGptService(config.ChatGPT_TOKEN)
app = ApplicationBuilder().token(config.BOT_TOKEN).build()

app.add_handler(CommandHandler('start', start))

# Random
app.add_handler(ConversationHandler(
    entry_points=[CommandHandler("random", random)],
    states={RandomState.RUNNING: [CallbackQueryHandler(random_button, pattern="^random_.*")]},
    fallbacks=[CommandHandler("start", start)]
))

# GPT
app.add_handler(ConversationHandler(
    entry_points=[CommandHandler("gpt", gpt)],
    states={GptState.RUNNING: [MessageHandler(filters.TEXT & ~filters.COMMAND, gpt_dialog)]},
    fallbacks=[CommandHandler("start", start)]
))

# Talk
app.add_handler(ConversationHandler(
    entry_points=[CommandHandler("talk", talk)],
    states={
        TalkState.CHOOSING_PERSON: [CallbackQueryHandler(talk_button, pattern="^talk_.*")],
        TalkState.TALKING: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, talk_dialog),
            CallbackQueryHandler(talk_button, pattern="^talk_end")
        ]
    },
    fallbacks=[CommandHandler("start", start)]
))

# Quiz
app.add_handler(ConversationHandler(
    entry_points=[CommandHandler("quiz", quiz)],
    states={
        QuizState.CHOOSING_QUIZ: [CallbackQueryHandler(quiz_button, pattern="^quiz_.*")],
        QuizState.QUIZ_RUNNING: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, quiz_dialog),
            CallbackQueryHandler(quiz_control, pattern="^quiz_.*")
        ]
    },
    fallbacks=[CommandHandler("start", start)]
))

# Translate
app.add_handler(ConversationHandler(
    entry_points=[CommandHandler("translate", translate)],
    states={
        TranslateState.CHOOSING_LANG: [CallbackQueryHandler(translate_button, pattern="^lang_.*")],
        TranslateState.TRANSLATING: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, translate_dialog),
            CallbackQueryHandler(translate_control, pattern="^(change_lang|translate_end)$")
        ]
    },
    fallbacks=[CommandHandler("start", start)]
))

#resume
app.add_handler(ConversationHandler(
    entry_points=[CommandHandler("resume", resume)],
    states={
        ResumeState.ASK_RESUME: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_resume)],
    },
    fallbacks=[CommandHandler("start", start)]
))

# Запуск
app.run_polling()