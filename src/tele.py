import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import os
from dotenv import load_dotenv

from orquestrador import agent_orquestrador
from agents.voice_agent import transcribe_voice

load_dotenv()

TOKEN_TELE = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_human = update.message.text
    chat_id = str(update.effective_chat.id)
    try:
        response = await agent_orquestrador(msg_human, chat_id)
        await context.bot.send_message(chat_id=chat_id, text=response)
    except Exception as e:
        print("erro:", e)
        raise


async def echo_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    chat_id = str(update.effective_chat.id)
    try:
        file_obj = await context.bot.get_file(update.message.voice.file_id)
        audio_bytes = await file_obj.download_as_bytearray()
        texto = await transcribe_voice(bytes(audio_bytes))
        response = await agent_orquestrador(texto, chat_id)
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text("Não consegui processar o áudio")
        print("erro:", e)


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN_TELE).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_handler(MessageHandler(filters.VOICE, echo_voice))

    app.run_polling()
