import os, asyncio, logging
from dotenv import load_dotenv
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
genai.configure(api_key=GEMINI_API_KEY)
SYSTEM_PROMPT = "Ban la tro ly AI thong minh, than thien. Hay tra loi bang tieng Viet."
chat_sessions = {}
logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

def get_chat(uid):
    if uid not in chat_sessions:
        model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=SYSTEM_PROMPT)
        chat_sessions[uid] = model.start_chat(history=[])
    return chat_sessions[uid]

async def cmd_start(update, context):
    await update.message.reply_text("Xin chao! Toi la AI assistant. Hay hoi gi do!")

async def cmd_clear(update, context):
    chat_sessions.pop(update.effective_user.id, None)
    await update.message.reply_text("Da xoa lich su!")

async def handle_msg(update, context):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        reply = get_chat(update.effective_user.id).send_message(update.message.text).text
    except Exception as e:
        reply = f"Loi: {e}"
    await update.message.reply_text(reply[:4096])

async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
    async with app:
        await app.start()
        await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
