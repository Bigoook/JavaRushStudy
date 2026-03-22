from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from states import RandomState, GptState, TalkState, QuizState, TranslateState, ResumeState
from util import show_mode_screen, show_main_menu, send_text, send_text_buttons, ask_gpt, load_prompt


# ====== Start ======

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_mode_screen(update, context, "main")
    await show_main_menu(update, context, {
        "start":     "Головне меню",
        "random":    "Дізнатися випадковий цікавий факт 🧠",
        "gpt":       "Задати питання чату GPT 🤖",
        "talk":      "Поговорити з відомою особистістю 👤",
        "quiz":      "Взяти участь у квізі ❓",
        "translate": "Перекладач 🌐",
        "resume":    "Допомога з резюме 📄",
    })
    return ConversationHandler.END


# ====== Random ======

async def random_start(update, context, chat_gpt):
    await show_mode_screen(update, context, "random")
    answer = await ask_gpt(chat_gpt, "random", "Згенеруй один цікавий факт прямо зараз.")
    await send_text_buttons(update, context, answer or "Не вдалося отримати факт 😔", {
        "random_end":  "Закінчити",
        "random_more": "Хочу ще факт",
    })
    return RandomState.RUNNING

async def random_button(update, context, chat_gpt):
    query = update.callback_query.data
    await update.callback_query.answer()
    if query == "random_end":
        return await start(update, context)
    return await random_start(update, context, chat_gpt)


# ====== GPT ======

async def gpt_start(update, context):
    await show_mode_screen(update, context, "gpt")
    return GptState.RUNNING

async def gpt_dialog(update, context, chat_gpt):
    text = update.message.text
    answer = await ask_gpt(chat_gpt, "gpt", text)
    await send_text(update, context, answer or "Не вдалося отримати відповідь 😔")
    return GptState.RUNNING


# ====== Talk ======

TALK_PERSONS = {
    "talk_cobain":    "Курт Кобейн",
    "talk_queen":     "Королева Єлизавета",
    "talk_tolkien":   "Дж.Р.Р. Толкін",
    "talk_nietzsche": "Фрідріх Ніцше",
    "talk_hawking":   "Стівен Гокінг",
}

async def talk_start(update, context):
    await show_mode_screen(update, context, "talk", TALK_PERSONS)
    return TalkState.CHOOSING_PERSON

async def talk_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()
    if query == "talk_end":
        return await start(update, context)
    await show_mode_screen(update, context, query, text="Готовий відповісти на всі ваші питання!")
    context.user_data["talk_topic"] = query
    return TalkState.TALKING

async def talk_dialog(update, context, chat_gpt):
    text = update.message.text
    topic = context.user_data.get("talk_topic", "talk_cobain")
    answer = await ask_gpt(chat_gpt, prompt_name=topic, user_text=text)
    await send_text_buttons(update, context, answer or "Нічого не скажу 😔", {
        "talk_end": "Закінчити",
    })
    return TalkState.TALKING


# ====== Quiz ======

QUIZ_TOPICS = {
    "quiz_prog":    "Програмування на Python",
    "quiz_math":    "Математика",
    "quiz_biology": "Біологія",
}

async def quiz_start(update, context):
    await show_mode_screen(update, context, "quiz", QUIZ_TOPICS)
    return QuizState.CHOOSING_QUIZ

async def quiz_button(update, context, chat_gpt):
    query = update.callback_query.data
    await update.callback_query.answer()
    context.user_data["quiz_topic"] = query
    msg = await send_text(update, context, "Готую питання!")
    answer = await ask_gpt(chat_gpt, prompt_name=load_prompt("quiz"), user_text=query)
    await msg.edit_text(answer or "Не придумав питання 😔")
    return QuizState.QUIZ_RUNNING

async def quiz_dialog(update, context, chat_gpt):
    text = update.message.text
    answer = await chat_gpt.add_message(text)
    if "Правильно!" in answer:
        context.user_data["quiz_score"] = context.user_data.get("quiz_score", 0) + 1
    score = context.user_data.get("quiz_score", 0)
    await send_text_buttons(update, context, f"{answer}\n\nВаш рахунок: {score}", {
        "quiz_more":   "Ще питання",
        "quiz_change": "Змінити тему",
        "quiz_end":    "Закінчити",
    })
    return QuizState.QUIZ_RUNNING

async def quiz_control(update, context, chat_gpt):
    query = update.callback_query.data
    await update.callback_query.answer()
    if query == "quiz_end":
        return await start(update, context)
    if query == "quiz_change":
        return await quiz_start(update, context)
    if query == "quiz_more":
        topic = context.user_data.get("quiz_topic", "quiz_prog")
        msg = await send_text(update, context, "Готую питання!")
        answer = await ask_gpt(chat_gpt, prompt_name=load_prompt("quiz"), user_text=topic)
        await msg.edit_text(answer or "Не придумав питання 😔")
    return QuizState.QUIZ_RUNNING


# ====== Translate ======

TRANSLATE_LANGS = {
    "lang_en": "Англійська",
    "lang_de": "Німецька",
    "lang_fr": "Французька",
    "lang_es": "Іспанська",
}

async def translate_start(update, context):
    await show_mode_screen(update, context, "translate", TRANSLATE_LANGS,
                           text="Обери мову, на яку потрібно перекласти текст:")
    return TranslateState.CHOOSING_LANG

async def translate_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()
    context.user_data["translate_lang"] = query
    await send_text(update, context, "Надішліть текст для перекладу.")
    return TranslateState.TRANSLATING

async def translate_dialog(update, context, chat_gpt):
    text = update.message.text
    lang = context.user_data.get("translate_lang", "lang_en")
    answer = await ask_gpt(chat_gpt, "translate", text, extra=f"Мова для перекладу: {lang}")
    await send_text_buttons(update, context, answer or "Не вдалося отримати переклад 😔", {
        "change_lang":   "Змінити мову",
        "translate_end": "Закінчити",
    })
    return TranslateState.TRANSLATING

async def translate_control(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()
    if query == "translate_end":
        return await start(update, context)
    if query == "change_lang":
        return await translate_start(update, context)
    return TranslateState.TRANSLATING


# ====== Resume ======

async def resume_start(update, context):
    await send_text(
        update, context,
        "Введіть одним повідомленням вашу освіту, досвід роботи та навички.\n"
        "Наприклад:\n"
        "Освіта: КНУ, комп'ютерні науки, 2015–2019\n"
        "Досвід роботи: SoftServe, Python Developer, 2019–2023\n"
        "Навички: Python, Django, SQL",
    )
    return ResumeState.ASK_RESUME

async def generate_resume(update, context, chat_gpt):
    user_data = update.message.text
    answer = await chat_gpt.send_question(
        prompt_text=load_prompt("resume"),
        message_text=user_data,
    )
    await send_text(update, context, answer or "Не вдалося сформувати резюме 😔")
    return ConversationHandler.END