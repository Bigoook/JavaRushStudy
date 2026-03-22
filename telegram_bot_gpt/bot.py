from telegram.ext import ApplicationBuilder, CommandHandler

from gpt import ChatGptService
from credentials import config
from handlers import start
from conversations import build_conversations

chat_gpt = ChatGptService(config.ChatGPT_TOKEN)

app = ApplicationBuilder().token(config.BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))

for conv in build_conversations(chat_gpt):
    app.add_handler(conv)

app.run_polling()
