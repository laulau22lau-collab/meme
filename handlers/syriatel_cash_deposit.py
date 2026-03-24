from iChancyAPI import iChancyAPI
import asyncio
import Logger , store
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update,ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackContext,
    MessageHandler,
    filters,
    CommandHandler,
    CallbackQueryHandler,
)
from services.transaction_notification_service import transaction_notification_service

logger = Logger.getLogger()

transfer_num, value = range(2)
# معالجة الضغط على الزر الداخلي
async def button_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == 'syriatel_cash_deposit':
        await query.edit_message_text(
            text=(
                "ارسل الى احد الارقام التالية بطريقة التحويل اليدوي\n"
                "14969577\n"
                "\n\n"
                "اقل قيمة للشحن هي 5,000\n"
                "وأي قيمة أقل من 5,000 لا يمكن شحنها او استرجاعها\n"
                "ثم ادخل رقم عملية التحويل  👇\n"
            )
        )
        return transfer_num

    return ConversationHandler.END

async def get_transfer_num(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    telegram_user_id = str(update.effective_user.id)
    transfer_num = update.message.text
    context.user_data['transfer_num'] = transfer_num
    logger.info("User %s entered transfer number: %s", user.first_name, transfer_num)
    await update.message.reply_text(
        f"ادخل المبلغ الذي ارسلته بالليرة السورية"
    )
    return value

async def get_value(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    value = update.message.text
    context.user_data['value'] = value
    logger.info("User %s set value: %s", user.first_name, value)
    asyncio.create_task(handle_create_transaction(update , context=context))
    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        'تم إلغاء عملية الشحن.',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def conversationHandler():
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern='^syriatel_cash_deposit$')],
        states={
            transfer_num: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_transfer_num)],
            value: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_value)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    return conv_handler

def getConfirmMarkup():
    keyboard = [
        [InlineKeyboardButton("تأكيد", callback_data='confirm_syriatel_cash_deposit')],
    ]
    return InlineKeyboardMarkup(keyboard)

async def confirm_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    syriatelCashTransactionId = context.user_data.get('syriatelCashTransactionId')
        # Send notification to admin about new transaction
    if syriatelCashTransactionId:
        await transaction_notification_service.notify_admin_new_transaction(syriatelCashTransactionId, 'syriatel')

    # Get the current message text and add success message
    current_text = query.message.text
    success_text = current_text + "\n✅ تم إرسال طلبك للمراجعة. سيتم إشعارك عند الموافقة أو الرفض."
    
    # Edit the message to remove the keyboard and add success message
    await query.edit_message_text(
        text=success_text,
        reply_markup=None,  # This removes the keyboard
        parse_mode='Markdown'
    )
    
    return ConversationHandler.END

async def handle_create_transaction(update: Update ,context: ContextTypes.DEFAULT_TYPE):
    """Handle account creation"""
    try:
        telegram_user_id = str(update.effective_user.id)
        transfer_num=context.user_data.get('transfer_num')
        value=context.user_data.get('value')
        api = iChancyAPI()
        logger.info(api.COOKIES)

        syriatelCashTransactionId = store.insertTransaction(telegram_id = telegram_user_id,value=value,action_type='deposit',provider_type='syriatel',transfer_num=transfer_num)

        # Store transaction ID in context for later use
        context.user_data['syriatelCashTransactionId'] = syriatelCashTransactionId

        success_text = (
            "طلب شحن\n"
            "Syriatel Cash 🟢\n"
            "رقم العملية او العنوان: " + str(transfer_num) + "\n\n"
            "المبلغ بالليرة:  " + str(value) + "\n"
            "قيمة الطلب: " + str(value) + "\n"
            "رقم الطلب: #" + str(syriatelCashTransactionId) + "\n\n"
        )
        
        await update.message.reply_text(success_text,reply_markup=getConfirmMarkup(), parse_mode='Markdown')

 
    except Exception as e:
        logger.error(f"Error in handle_create_transaction: {e}")
  
    context.user_data.pop('transfer_num', None)
    context.user_data.pop('value', None)
