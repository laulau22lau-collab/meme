import handlers.checkStatus , handlers.ichancy 
import handlers.backToMenu, handlers.help, handlers.withdrawal, handlers.deposit ,handlers.conditions , handlers.problemInBot ,handlers.problemInWebsite
import handlers.contactUs
import handlers.guidesHandlers.guides , handlers.guidesHandlers.guidesWhatIchancy
import handlers.guidesHandlers.guidesHowToCreateNewAccount
import handlers.guidesHandlers.guidesHowDepositTelegramAccount
import handlers.guidesHandlers.guidesHowWithdrawTelegramAccount
import handlers.guidesHandlers.guidesHowDepositIchancyAccount
import handlers.guidesHandlers.guidesHowWithdrawIchancyAccount
import handlers.syriatel_cash_deposit
import handlers.transactions
from telegram import Update
from telegram.ext import ContextTypes
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline keyboard button presses"""
    query = update.callback_query
    await query.answer() 
    user_id = str(update.effective_user.id)
    username = update.effective_user.username
    data = query.data
    
    if data.find('guide') != -1:
        await guidesButton(update , context , query)
    elif data == 'check_status':
        await handlers.checkStatus.handle_check_status(query, user_id)
    elif data == 'help':
        await handlers.help.handle_help(query)
    elif data == 'back_to_menu':
        await handlers.backToMenu.handle_back_to_menu(query ,username)
    elif data == 'ichancy':
        await handlers.ichancy.handle_ichancy(query , user_id)
    elif data == 'withdrawal':
        await handlers.withdrawal.handle_withdrawal(query , user_id)
    elif data == 'deposit':
        await handlers.deposit.handle_deposit(query , user_id)
    elif data == 'terms_and_conditions':
        await handlers.conditions.handle_terms_and_conditions(query)
    elif data == 'contact_us':
        await handlers.contactUs.handle_contact_us(query)
    elif data =='problem_in_bot':
         await handlers.problemInBot.handle_problem_in_bot(query)
    elif data =='problem_in_website':
         await handlers.problemInWebsite.handle_problem_in_website(query)

    elif data == 'confirm_syriatel_cash_deposit':
        await handlers.syriatel_cash_deposit.confirm_deposit(update, context)
    elif data.startswith('approve_'):
        _, transaction_type, transaction_id = data.split('_')
        await handlers.transactions.approve_transaction(query, transaction_id,transaction_type)
    elif data.startswith('reject_'):
        _, transaction_type, transaction_id = data.split('_')
        await handlers.transactions.reject_transaction(query, transaction_id, transaction_type)

async def guidesButton(update: Update, context: ContextTypes.DEFAULT_TYPE , query):
    data = query.data
    if data == "guides":
        await handlers.guidesHandlers.guides.handle_guides(query)
    elif data == "guides_what_is_ichancy":
        await handlers.guidesHandlers.guidesWhatIchancy.handle_guides_what_is_ichancy(query)
    elif data == "guides_how_deposit_telegram_account":
        await handlers.guidesHandlers.guidesHowDepositTelegramAccount.handle_guides_how_deposit_telegram_account(query)
    elif data == "guides_how_to_create_new_account":
        await handlers.guidesHandlers.guidesHowToCreateNewAccount.handle_guides_how_to_create_new_account(query)
    elif data == "guides_how_withdraw_telegram_account":
        await handlers.guidesHandlers.guidesHowWithdrawTelegramAccount.handle_guides_how_withdraw_telegram_account(query)
    elif data == "guides_how_deposit_ichancy_account":
        await handlers.guidesHandlers.guidesHowDepositIchancyAccount.handle_guides_how_deposit_ichancy_account(query)
    elif data == "guides_how_withdraw_ichancy_account":
        await handlers.guidesHandlers.guidesHowWithdrawIchancyAccount.handle_guides_how_withdraw_ichancy_account(query)
