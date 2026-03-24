import string
from iChancyAPI import iChancyAPI
import asyncio
import Logger , store
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup,ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackContext,
    MessageHandler,
    filters,
    CommandHandler,
    CallbackQueryHandler,
)
import random

logger = Logger.getLogger()

USERNAME, PASSWORD = range(2)
# معالجة الضغط على الزر الداخلي
async def button_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == 'create_account':
        await query.edit_message_text(
            text="Enter User name....\nاسم المستخدم"
        )
        return USERNAME

    return ConversationHandler.END

# استقبال اسم المستخدم
async def get_username(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    telegram_id = str(update.effective_user.id)
    username = update.message.text 
    email = username + "@meme.com"
    context.user_data['email'] = email
    context.user_data['username'] = username
    logger.info("User %s chose username: %s", user.first_name, username)
    await update.message.reply_text(
        f"Enter Password..\nادخل كلمة السر"
    )
    return PASSWORD

# استقبال كلمة المرور
async def get_password(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    password = update.message.text
    context.user_data['password'] = password
    logger.info("User %s set password: %s", user.first_name, password)
    asyncio.create_task(handle_create_account(update , context=context))
    return ConversationHandler.END


# إلغاء المحادثة
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        'تم إلغاء عملية إنشاء الحساب.',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def conversationHandler():
    conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(button_handler, pattern='^create_account$')],
    states={
        USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username)],
        PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
    )    
    return conv_handler
async def handle_create_account(update: Update ,context: ContextTypes.DEFAULT_TYPE):
    """Handle account creation"""
    try:
        user_id = str(update.effective_user.id)
        email=context.user_data.get('email')
        username=context.user_data.get('username')
        password=context.user_data.get('password')
        api = iChancyAPI()
        logger.info(api.COOKIES)
        result = api.register_account(email=email, username=username, password=password)


        count = 1
        while not result['success'] and count <15:
            count+=1
            username=context.user_data.get('username')+ "_"+ ''.join(random.choices(string.ascii_letters + string.digits,k=3))
            email = username + "@meme.com"
            result = api.register_account(email=email, username=username, password=password)


        if result['success']:
            playerId = api.getPlayerId(username)    
            store.insertUserDetailes(telegram_id = user_id,name = username,password=password,email=email , player_id = playerId)
            keyboard = [[InlineKeyboardButton("🏠 Back to Menu", callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            success_text = (
                f"✅ **تم إنشاءالحساب بجاح !** \n\n"
                f"🆔 **الدخول**: `{result['username']}`\n"
                f"🔒 **كلمة المرور**: `{result['password']}`\n"
                f"📧 **الإيميل**: `{result['email']}`\n"
            )
            
            await update.message.reply_text(success_text ,parse_mode='Markdown')
        else:
            keyboard = [[InlineKeyboardButton("🔄 Try Again", callback_data='create_account'),
                        InlineKeyboardButton("🏠 Menu", callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Clean error message for Telegram
            error_msg = result['error']
            # Remove or escape special characters that break Markdown
            error_msg = error_msg.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]').replace('(', '\\(').replace(')', '\\)').replace('~', '\\~').replace('`', '\\`').replace('>', '\\>').replace('#', '\\#').replace('+', '\\+').replace('-', '\\-').replace('=', '\\=').replace('|', '\\|').replace('{', '\\{').replace('}', '\\}').replace('.', '\\.').replace('!', '\\!')
            keyboard = [[InlineKeyboardButton("🏠 Back to Menu", callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"❌ **Account Creation Failed**\n\n"
                f"Error: {error_msg}\n\n"
                "You can try again or return to the main menu.",
                reply_markup=reply_markup,
                parse_mode='Markdown'
                
            )
    except Exception as e:
        logger.error(f"Error in handle_create_account: {e}")
        keyboard = [[InlineKeyboardButton("🏠 Back to Menu", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"❌ **An error occurred**: {str(e)}",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    context.user_data.pop('username', None)
    context.user_data.pop('password', None)
    context.user_data.pop('email', None)
