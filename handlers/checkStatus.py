import store
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import time
import helpers


async def handle_check_status(query, user_id):
    """Check account status"""
    
    user = store.getUserByTelegramId(user_id)

    if not user:
        keyboard = [[InlineKeyboardButton("🆕 Create Account", callback_data='create_account'),
                    InlineKeyboardButton("🏠 Menu", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "❌ **لا يوجد حساب بعد**\n\n"
            "أنت لا تمتلك حساب.\n"
            "أنشئ حساب اولا",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return
    created_time = user['created_at'].strftime('%Y-%m-%d %H:%M:%S')
    
    keyboard = [[InlineKeyboardButton("🏠 Back to Menu", callback_data='back_to_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    

    
    await query.edit_message_text(helpers.getStatusText(user), reply_markup=reply_markup)
