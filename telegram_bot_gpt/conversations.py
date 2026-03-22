from functools import partial

from telegram.ext import (
    ConversationHandler, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters
)

from states import RandomState, GptState, TalkState, QuizState, TranslateState, ResumeState
from handlers import (
    start,
    random_start, random_button,
    gpt_start, gpt_dialog,
    talk_start, talk_button, talk_dialog,
    quiz_start, quiz_button, quiz_dialog, quiz_control,
    translate_start, translate_button, translate_dialog, translate_control,
    resume_start, generate_resume,
)


def build_conversations(chat_gpt) -> list:
    p = partial  # коротший аліас

    return [
        # Random
        ConversationHandler(
            entry_points=[CommandHandler("random", p(random_start, chat_gpt=chat_gpt))],
            states={
                RandomState.RUNNING: [
                    CallbackQueryHandler(p(random_button, chat_gpt=chat_gpt), pattern="^random_.*"),
                ],
            },
            fallbacks=[CommandHandler("start", start)],
        ),

        # GPT
        ConversationHandler(
            entry_points=[CommandHandler("gpt", gpt_start)],
            states={
                GptState.RUNNING: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, p(gpt_dialog, chat_gpt=chat_gpt)),
                ],
            },
            fallbacks=[CommandHandler("start", start)],
        ),

        # Talk
        ConversationHandler(
            entry_points=[CommandHandler("talk", talk_start)],
            states={
                TalkState.CHOOSING_PERSON: [
                    CallbackQueryHandler(talk_button, pattern="^talk_.*"),
                ],
                TalkState.TALKING: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, p(talk_dialog, chat_gpt=chat_gpt)),
                    CallbackQueryHandler(talk_button, pattern="^talk_end$"),
                ],
            },
            fallbacks=[CommandHandler("start", start)],
        ),

        # Quiz
        ConversationHandler(
            entry_points=[CommandHandler("quiz", quiz_start)],
            states={
                QuizState.CHOOSING_QUIZ: [
                    CallbackQueryHandler(p(quiz_button, chat_gpt=chat_gpt), pattern="^quiz_.*"),
                ],
                QuizState.QUIZ_RUNNING: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, p(quiz_dialog, chat_gpt=chat_gpt)),
                    CallbackQueryHandler(p(quiz_control, chat_gpt=chat_gpt), pattern="^quiz_.*"),
                ],
            },
            fallbacks=[CommandHandler("start", start)],
        ),

        # Translate
        ConversationHandler(
            entry_points=[CommandHandler("translate", translate_start)],
            states={
                TranslateState.CHOOSING_LANG: [
                    CallbackQueryHandler(translate_button, pattern="^lang_.*"),
                ],
                TranslateState.TRANSLATING: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, p(translate_dialog, chat_gpt=chat_gpt)),
                    CallbackQueryHandler(translate_control, pattern="^(change_lang|translate_end)$"),
                ],
            },
            fallbacks=[CommandHandler("start", start)],
        ),

        # Resume
        ConversationHandler(
            entry_points=[CommandHandler("resume", resume_start)],
            states={
                ResumeState.ASK_RESUME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, p(generate_resume, chat_gpt=chat_gpt)),
                ],
            },
            fallbacks=[CommandHandler("start", start)],
        ),
    ]
