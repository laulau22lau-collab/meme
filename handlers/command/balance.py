import store
from telegram import Update
from telegram.ext import ContextTypes

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Balance command handler"""
    user_id = str(update.effective_user.id)
    user = store.getUserByTelegramId(user_id)
    if not user:
        await update.message.reply_text("You don't have any account.")
        return

    await update.message.reply_text(f"Your balance is {user.get('balance', 0)}\nYour telegram id is {user.get('telegram_id', 'N/A')}")
