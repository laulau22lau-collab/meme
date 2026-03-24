import os
import requests
import logging
from dotenv import load_dotenv

# تحميل الإعدادات من ملف .env
load_dotenv()

# إعداد اللوجر (Logger) لمراقبة الأخطاء
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("iChancyAPI")

class iChancyAPI:
    BASE_URL = 'https://agents.ichancy.com'
    
    def __init__(self):
        self.session = requests.Session()
        # جلب الكوكي من ملف .env
        self.cookie_string = os.getenv("ICHANCY_COOKIE")
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Cookie': self.cookie_string,
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Origin': 'https://agents.ichancy.com',
            'Referer': 'https://agents.ichancy.com/',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.session.headers.update(self.headers)
        logger.info("✅ تم تهيئة API كاشيرة iChancy بنجاح")

    def getAdminstratorBalance(self):
        """جلب رصيد الكاشيرة (الأدمن)"""
        url = f"{self.BASE_URL}/global/api/Agent/getAgentWalletByAgentId"
        # PARENT_ID هو نفسه الأي دي تبع حسابك بالكاشيرة
        payload = {
            'affiliateId': os.getenv("PARENT_ID", "12345"), # حط الـ ID تبعك بالـ .env أو هون
            'currencyCode': "NSP"
        }
        try:
            response = self.session.post(url, json=payload, timeout=30)
            data = response.json()
            if data.get('result'):
                return int(data['result'].get('balance', 0))
            return 0
        except Exception as e:
            logger.error(f"❌ خطأ في جلب رصيد الأدمن: {e}")
            return 0

    def register_account(self, username, password, email):
        """إنشاء حساب لاعب جديد"""
        url = f"{self.BASE_URL}/global/api/Player/registerPlayer"
        payload = {
            "player": {
                "login": username,
                "email": email,
                "password": password,
                "parentId": os.getenv("PARENT_ID")
            }
        }
        try:
            response = self.session.post(url, json=payload, timeout=30)
            data = response.json()
            if data.get("result"):
                return {'success': True, 'data': data['result']}
            error_msg = data.get("notification", [{}])[0].get("content", "خطأ غير معروف")
            return {'success': False, 'error': error_msg}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def transfeerMoney(self, player_id, amount, comment="Transfer from Bot"):
        """شحن رصيد للاعب (Deposit)"""
        url = f"{self.BASE_URL}/global/api/Player/depositToPlayer"
        payload = {
            'amount': amount,
            'comment': comment,
            'playerId': player_id,
            'currencyCode': "NSP",
            'moneyStatus': 5
        }
        try:
            response = self.session.post(url, json=payload, timeout=30)
            return response.json()
        except Exception as e:
            logger.error(f"❌ فشل تحويل المبلغ: {e}")
            return {'success': False, 'error': str(e)}

    def withdrawMoney(self, player_id, amount, comment="Withdraw from Bot"):
        """سحب رصيد من لاعب (Withdraw)"""
        url = f"{self.BASE_URL}/global/api/Player/withdrawFromPlayer"
        # في السحب لازم تكون القيمة سالبة
        payload = {
            'amount': -abs(amount),
            'comment': comment,
            'playerId': player_id,
            'currencyCode': "NSP",
            'moneyStatus': 5
        }
        try:
            response = self.session.post(url, json=payload, timeout=30)
            return response.json()
        except Exception as e:
            logger.error(f"❌ فشل سحب المبلغ: {e}")
            return {'success': False, 'error': str(e)}

# تجربة التشغيل
if __name__ == "__main__":
    bot_api = iChancyAPI()
    balance = bot_api.getAdminstratorBalance()
    print(f"💰 رصيد الكاشيرة الحالي هو: {balance}")
