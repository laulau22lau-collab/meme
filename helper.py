import Logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import ContextTypes
logger = Logger.getLogger()
def getTextWelcome(username):
    welcome_text = (
            f"أهلا بك في بوت\n "
             "mera ichancey"
        )
    return welcome_text

def getKeyboard():
    keyboard = [
        [InlineKeyboardButton("⚡️ Ichancy", callback_data='ichancy')],
        [
            InlineKeyboardButton("شحن رصيد 📥", callback_data='deposit'),
            InlineKeyboardButton("سحب رصيد 📤", callback_data='withdrawal'),
        ],
        [InlineKeyboardButton("نظام الاحالات 💰", callback_data='referral')],
        [
            InlineKeyboardButton("اهداء رصيد 🎁", callback_data='send_gift'),
            InlineKeyboardButton("كود هدية 🎁", callback_data='reseive_gift'),
        ],
        [
            InlineKeyboardButton("رسالة للادمن 📨", callback_data='admin_message'),
            InlineKeyboardButton("تواصل معنا ✉️", callback_data='contact_us'),
        ],
        [
            InlineKeyboardButton("السجل 📜", callback_data='log'),
            InlineKeyboardButton("الشروحات 📝", callback_data='guides'),
        ],
        [InlineKeyboardButton("الشروط والاحكام 📌", callback_data='terms_and_conditions')],
        # [InlineKeyboardButton("📊 Check Account Status", callback_data='check_status')],
        # [InlineKeyboardButton("❓ Help", callback_data='help')],
    ]
    return keyboard,

def getReplyMarkup():
    reply_markup = InlineKeyboardMarkup(getKeyboard())
    return reply_markup

async def getInfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or update.effective_user.first_name
    logger.info(f"User {username} ({user_id}) started the bot")
    return user_id , username

def getStatusText(user):
    status_text = (
        "https://www.ichancy.com/ar \n\n"
        f"👤 الدخول: {user['name']}\n"
        f"📧 الإيميل: {user['email']}\n"
        f"🔒 كلمة السر: {user['password']} "
    )
    return status_text
