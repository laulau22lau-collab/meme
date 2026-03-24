from telegram import Update ,ReplyKeyboardRemove 
from iChancyAPI import iChancyAPI
from telegram.ext import ConversationHandler , ContextTypes , MessageHandler ,filters ,CallbackQueryHandler ,CommandHandler ,CallbackContext
import store
import config.ichancy
AMMOUNT = range(1)

async def button_deposit_account_handler(update : Update , context : ContextTypes.DEFAULT_TYPE):
    telegram_id = update.callback_query.from_user.id
    user = store.getUserByTelegramId(telegram_id)
    playerId = user.get('player_id')
    account_balance = user.get('account_balance')
    balance = user.get('balance')
    context.user_data['player_id'] = playerId
    context.user_data['balance'] = balance
    context.user_data['telegram_id'] = telegram_id
    context.user_data['account_balance'] = account_balance

    await update.callback_query.edit_message_text("ادخل المبلغ المراد تحويله")
    return AMMOUNT


async def get_ammount_for_deposit(update: Update , context : ContextTypes.DEFAULT_TYPE):
    ammountForDeposit = int(update.message.text)
    playerId= context.user_data.get('player_id')
    telegram_id = context.user_data.get('telegram_id')
    balance = context.user_data['balance']
    account_balance = context.user_data['account_balance']
    if balance*config.ichancy.EXCHANGE_RATE  < ammountForDeposit:
        await update.message.reply_text("فشلت العملية ليس معك رصيد كافٍ!")
        return ConversationHandler.END
    api = iChancyAPI()
    adminBalance = api.getAdminstratorBalance()
    if adminBalance < ammountForDeposit:
        await update.message.reply_text("فشلت العملية!")
        return ConversationHandler.END
    newBlanceForPlaryer = balance - ammountForDeposit*config.ichancy.EXCHANGE_RATE 
    newAccountBalance = account_balance + ammountForDeposit*config.ichancy.EXCHANGE_RATE
    store.insertNewBalance(telegram_id,newBlanceForPlaryer)
    store.insertNewAccountBalance(telegram_id,newAccountBalance)
    user_id = store.getUserIdByTelegramId(telegram_id).get('id')
    store.insertInTransactionAccount(user_id,'done','deposit',ammountForDeposit)
    api.transfeerMoney(ammount=ammountForDeposit, player_id=playerId)
    await update.message.reply_text("تمت العملية بنجاح")
    return ConversationHandler.END
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "تم إالغاء عملية الإيداع",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def conversationHandler():
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_deposit_account_handler , pattern = "^deposit_account$")],
        states={
            AMMOUNT :[MessageHandler(filters.TEXT & ~filters.COMMAND , get_ammount_for_deposit)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    return conv_handler
