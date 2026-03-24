from telegram import CallbackQuery ,Update ,ReplyKeyboardRemove
from telegram.ext import ConversationHandler , CallbackQueryHandler ,MessageHandler ,filters ,CallbackContext ,CommandHandler
import store
CODE = range(1)

async def button_reseive_gift_handler(update: Update , context:CallbackContext ):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("يرجى إدخال الكود المخصص للهدية")
    return CODE

async def get_code(update:Update , context:CallbackContext):
    
    code = update.message.text
    telegram_id = update.message.from_user.id
    print(telegram_id)
    status = store.getGift(code,telegram_id)
    if status:
        await update.message.reply_text("تمت العملية بنجاح")
    else:
        await update.message.reply_text("الكود الذي تم إدخاله غير صحيح")
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        'تم إلغاء عملية إهداء الرصيد',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def conversationHandler():
    conv_handler = ConversationHandler(
        entry_points= [CallbackQueryHandler(button_reseive_gift_handler , pattern='^reseive_gift$')],
        states={
            CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND , get_code)]
        },
     fallbacks=[CommandHandler('cancel', cancel)],
    )
    return conv_handler
