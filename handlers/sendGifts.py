import string
from iChancyAPI import iChancyAPI
import asyncio
import Logger , store , helpers
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
async def getText(update , context):
    telegram_id , username = await helpers.getInfo(update , context)
    text = (
    " يمكن الحصول على المعرف عن طريق ضغط زر رصيد"
    f"معرف الاهداء الخاص بك هو {telegram_id}\n"
    "ارسل معرف تلغرام المستخدم الذي تريد اهداؤه\n"
    )
    return text
telegramIdGoal, ammount = range(2)
# معالجة الضغط على الزر الداخلي
async def button_send_gifts_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    text = await getText(update , context)
    if query.data == 'send_gift':
        await query.edit_message_text(
            text=text ,
            parse_mode='Markdown'
        )
        return telegramIdGoal

    return ConversationHandler.END


async def get_telegram_id_goal(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    telegram_id = str(update.effective_user.id)
    telegramIdGoal = update.message.text 
    context.user_data['telegramIdGoal'] = telegramIdGoal
    userAcount = store.getUserByTelegramId(telegram_id)
    logger.info("User %s chose telegramIdGoal: %s", user.first_name, telegramIdGoal)

    if not userAcount.get('balance') or userAcount.get('balance') == 0:
        await update.message.reply_text(
        f"ليس لديك رصيد للإهداء"
    )
        return ConversationHandler.END
    await update.message.reply_text(
        f"أدخل الكمية المراد إهداؤها"
    )
    return ammount

async def get_gift_ammount(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    telegram_id = str(update.effective_user.id)
    ammount = update.message.text 
    context.user_data['gift_ammount'] = ammount
    telegramIdGoal = context.user_data.get('telegramIdGoal')
    logger.info("User %s chose gift_ammount: %s", user.first_name, ammount)
    code = ''.join(random.choices(string.ascii_letters + string.digits,k=20))
    status =store.insertGift(telegram_id,ammount,telegramIdGoal,code)
    if status:
        await update.message.reply_text(
            "تمت العملية بنجاح ! \n\n"
            "كود الهدية هو : \n\n"
            f"`{code}` \n\n"
            "يمكنك استخدامه للحصول على الهدية",parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "ليس لديك رصيد كافِ \n\n"
            "يرجى تعبئة الرصيد"
        )
    return ConversationHandler.END


# إلغاء المحادثة
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        'تم إلغاء عملية إهداء الرصيد',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def conversationHandler():
    print("________________________________________________________")
    conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(button_send_gifts_handler, pattern='^send_gift$')],
    states={
        telegramIdGoal: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_telegram_id_goal)],
        ammount: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gift_ammount)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
    )    
    return conv_handler
