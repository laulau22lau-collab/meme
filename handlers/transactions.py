import Logger
import store
import config.telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime

import trans

logger = Logger.getLogger()

async def approve_transaction(query, transaction_id, transaction_type):
    print("++++++++++++++++++++++++ approve_transaction +++++++++++++++++++++++++++++++++++++")
    """Approve a transaction"""
    try:
        # Update transaction status in database
        success = store.update_transaction_status(transaction_id, transaction_type, 'approved')
        
        if success:
            # Get transaction details
            transaction = store.get_transaction_by_id(transaction_id, transaction_type)
            if transaction:
                # Update user balance if it's a deposit
                if transaction['action_type'] == 'deposit':
                    user_balance = store.get_user_balance(transaction['user_id'])
                    new_balance = user_balance + transaction['value']
                    store.update_user_balance(transaction['user_id'], new_balance)

                # Notify user about approval
                await notify_user_transaction_status(transaction, 'approved')
                
                await query.edit_message_text(
                    f"✅ تم قبول الطلب #{transaction_id} بنجاح!\n"
                )
            else:
                await query.edit_message_text("❌ الطلب غير موجود.")
        else:
            await query.edit_message_text("❌ فشل قبول الطلب.")
            
    except Exception as e:
        logger.error(f"Error approving transaction {transaction_id}: {e}")
        await query.edit_message_text("❌ هناك خطأ حدث اثناء قبول الطلب.")

async def reject_transaction(query, transaction_id, transaction_type):
    """Reject a transaction"""
    try:
        # Update transaction status in database
        success = store.update_transaction_status(transaction_id, transaction_type, 'rejected')
        
        if success:
            # Get transaction details
            transaction = store.get_transaction_by_id(transaction_id, transaction_type)
            if transaction:
                # Notify user about rejection
                await notify_user_transaction_status(transaction, 'rejected')
                
                await query.edit_message_text(
                    query.message.text + "\n" +
                    f"❌ تم رفض الطلب رقم #{transaction_id}.\n"
                    f"سيتم إعلام المستخدم برفض الطلب."
                )
            else:
                await query.edit_message_text("❌ الطلب غير موجود.")
        else:
            await query.edit_message_text("❌ فشل في رفض الطلب.")
            
    except Exception as e:
        logger.error(f"Error rejecting transaction {transaction_id}: {e}")
        await query.edit_message_text("❌ حدث خطأ أثناء رفض الطلب.")

async def show_pending_transactions(update, context):
    """Show all pending transactions"""
    try:
        pending_transactions = store.get_pending_transactions()
        
        if not pending_transactions:
            await update.message.reply_text("📭 No pending transactions.")
            return
        
        message = "📋 Pending Transactions:\n\n"
        
        for i, transaction in enumerate(pending_transactions[:10], 1):  # Limit to 10 transactions
            user = store.getUserById(transaction['user_id'])
            user_info = f"@{user[2]}" if user and user[2] else "No username"
            
            message += f"{i}. #{transaction['id']} - {user_info}\n"
            message += f"   💰 {transaction['value']} SYP - {transaction['action_type'].title()}\n"
            message += f"   📅 {transaction['created_at']}\n\n"
        
        keyboard = []
        for transaction in pending_transactions[:10]:
            keyboard.append([
                InlineKeyboardButton(
                    f"View #{transaction['id']}", 
                    callback_data=f'view_{transaction["id"]}'
                )
            ])
        
        keyboard.append([InlineKeyboardButton("🔄 Refresh", callback_data='refresh_pending')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error showing pending transactions: {e}")
        await update.message.reply_text("❌ Error occurred while fetching pending transactions.")

async def notify_user_transaction_status(transaction, status):
    """Send notification to user about transaction status"""
    try:
        from telegram import Bot
        from config.telegram import TOKEN
        
        bot = Bot(token=TOKEN)
        user_telegram_id = store.getTelegramIdByUserId(transaction['user_id'])
        
        if not user_telegram_id:
            logger.warning(f"Could not find telegram ID for user {transaction['user_id']}")
            return
        
        status_emoji = {
            'approved': '✅',
            'rejected': '❌'
        }.get(status, '❓')
        
        action_type_ar = trans.trans['ar'].get(transaction['action_type'], transaction['action_type'])
        status_ar = trans.trans['ar'].get(status, status)
        
        message = f"""
{status_emoji} تمت مراجعة الطلب

🆔 رقم الطلب: #{transaction['id']}
💰 المبلغ: {transaction['value']} SYP
📝 نوع التحويل: {action_type_ar}
📊 الحالة: {status_emoji} {status_ar}

{'تم تحديث رصيدك.' if status == 'approved' and transaction['action_type'] == 'deposit' else 'الرجاء التواصل معنا لاي استفسار.'}
        """
        
        await bot.send_message(chat_id=user_telegram_id, text=message)
        
    except Exception as e:
        logger.error(f"Error notifying user about transaction status: {e}")

async def send_transaction_to_admin(transaction_data, transaction_type):
    """Send transaction notification to admin for approval"""
    try:
        from telegram import Bot
        from config.telegram import TOKEN, ADMIN_TELEGRAM_ID, ADMIN_CHAT_ID
        import trans
        
        bot = Bot(token=TOKEN)
        
        user = store.getUserById(transaction_data['user_id'])
        user_info = f"@{user[2]}" if user and user[2] else "No username"
        
        # Get Arabic translation for action type
        action_type_ar = trans.trans['ar'].get(transaction_data['action_type'], transaction_data['action_type'])
        
        message = f"""
🆕 طلب {action_type_ar} جديد

🆔 رقم الطلب: #{transaction_data['id']}
📌 طريقة التحويل: {transaction_type}
👤 العضو: {user_info}
💰 المبلغ: {transaction_data['value']} SYP
📅 تاريخ الإنشاء: {transaction_data['created_at']}
        """
        
        if 'transfer_num' in transaction_data and transaction_data['transfer_num']:
            message += f"\n🔢 رقم عملية التحويل: {transaction_data['transfer_num']}"
        
        keyboard = [
            [
                InlineKeyboardButton("✅ تأكيد", callback_data=f'approve_{transaction_type}_{transaction_data["id"]}'),
                InlineKeyboardButton("❌ رفض", callback_data=f'reject_{transaction_type}_{transaction_data["id"]}')
            ],
            # [InlineKeyboardButton("👁️ View Details", callback_data=f'view_{transaction_data["id"]}')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Prefer ADMIN_CHAT_ID (e.g., a group) if provided to avoid 403 when admin hasn't started the bot
        target_chat_id = ADMIN_CHAT_ID if ADMIN_CHAT_ID else ADMIN_TELEGRAM_ID
        try:
            await bot.send_message(chat_id=target_chat_id, text=message, reply_markup=reply_markup)
        except Exception as e:
            # Common case: Forbidden: bot can't initiate conversation with a user
            err_text = str(e)
            if 'Forbidden' in err_text and 'initiate conversation' in err_text and not ADMIN_CHAT_ID:
                logger.error("Transactions bot can't message ADMIN_TELEGRAM_ID. Ask the admin to open the transactions bot and press /start, or set ADMIN_CHAT_ID to a group the bot is in.")
            raise
        
    except Exception as e:
        logger.error(f"Error sending transaction to admin: {e}")
