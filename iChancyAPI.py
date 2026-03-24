
import config.telegram ,config.ichancy ,config.device
import Logger
import requests

logger = Logger.getLogger()
class iChancyAPI:
    BASE_URL = 'https://www.ichancy.com'
    
    # Static headers - update these as needed
    HEADERS = {
        'User-Agent': config.device.USER_AGENT,
        'Cookie': config.telegram.COOKIE_STRING,
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://agents.ichancy.com',
        'Referer': 'https://agents.ichancy.com/'
    }
    
    @staticmethod
    def parse_cookie_string(cookie_string):
        """
        Parse a cookie string and return a dictionary of cookies
        Example: '__cf_bm=value1; cf_clearance=value2'
        """
        cookies = {}
        if not cookie_string:
            return cookies
            
        # Split by semicolon and process each cookie
        cookie_pairs = cookie_string.split(';')
        for pair in cookie_pairs:
            pair = pair.strip()
            if '=' in pair:
                name, value = pair.split('=', 1)
                cookies[name.strip()] = value.strip()
        
        return cookies
    
    @classmethod
    def set_cookies_from_string(cls, cookie_string):
        """
        Set cookies from a cookie string
        """
        cls.COOKIES = cls.parse_cookie_string(cookie_string)
        logger.info(f"Updated cookies: {list(cls.COOKIES.keys())}")
    
    def __init__(self):
        
        self.session = requests.Session()
        
        self.session.headers.update(self.HEADERS)

        self.set_cookies_from_string(config.telegram.COOKIE_STRING)
        
        logger.info("Initialized iChancy API with headers and cookies")
        
    def register_account(self, username=None, password=None, email=None, parent_id=config.ichancy.PARENT_ID):
        """
        Register a new account using the iChancy API
        """
        logger.info("Starting account registration process")
        
        try:
            
            logger.info(f"Generated credentials - Username: {username}, Email: {email}")
            
            # API endpoint
            register_url = "https://agents.ichancy.com/global/api/Player/registerPlayer"
            
            # Prepare JSON payload
            payload = {
                "player": {
                    "login": username,
                    "email": email,
                    "password": password,
                    "parentId": parent_id
                }
            }
            
            
            # Log the request details for debugging
            logger.info(f"Making request to: {register_url}")
            # logger.info(f"Headers: {headers}")
            logger.info(f"Payload: {payload}")
        
            # Submit registration
            logger.info("Submitting registration to API")
            try:
                response = self.session.post(
                    register_url, 
                    json=payload, 
                    timeout=30
                )
                # Log response details for debugging
                logger.info(f"Response status: {response.status_code}")
                logger.info(f"Response headers: {dict(response.headers)}")
                logger.info(f"Response text: {response.text[:500]}...")  # First 500 chars
                json = response.json()
                if not json.get("result"):
                    return {'success': False, 'error':json.get("notification")[0].get("content") }
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP Error: {e}")
                logger.error(f"Response status: {e.response.status_code}")
                
                # Check if it's a Cloudflare challenge
                if 'cf-mitigated' in e.response.headers and e.response.headers['cf-mitigated'] == 'challenge':
                    return {'success': False, 'error': 'Cloudflare challenge detected - cookies may be expired or invalid. Please get fresh cookies from your browser and update the COOKIE_STRING variable.'}
                
                # Try to decode response text safely
                try:
                    response_text = e.response.text[:200]
                except:
                    response_text = "Unable to decode response"
                
                return {'success': False, 'error': f'HTTP Error {e.response.status_code}: {response_text}'}
            except Exception as e:
                logger.error(f"Registration submission failed: {e}")
                return {'success': False, 'error': f'Registration submission failed: {str(e)}'}
            
            # Parse JSON response
            try:
                response_data = response.json()
                logger.info(f"API Response: {response_data}")
            except Exception as e:
                logger.error(f"Failed to parse JSON response: {e}")
                return {'success': False, 'error': 'Failed to parse API response'}
            
            # Check for success in API response
            if response.status_code == 200:
                # Check for success indicators in the response
                if isinstance(response_data, dict):
                    # Look for common success patterns
                    if response_data.get('success') is True or response_data.get('status') == 'success':
                        logger.info(f"Registration successful for username: {username}")
                        return {
                            'success': True,
                            'username': username,
                            'password': password,
                            'email': email,
                            'parent_id': parent_id,
                            'response': response_data,
                            'cookies': self.session.cookies.get_dict()
                        }
                    elif response_data.get('error') or response_data.get('message'):
                        error_msg = response_data.get('error') or response_data.get('message')
                        logger.warning(f"Registration failed: {error_msg}")
                        return {'success': False, 'error': error_msg}
                
                    # If response is not a dict or doesn't have clear success/error indicators
                    logger.info("Registration completed (API returned 200 OK)")
                    return {
                        'success': True,
                        'username': username,
                        'password': password,
                        'email': email,
                        'parent_id': parent_id,
                        'response': response_data,
                        'cookies': self.session.cookies.get_dict()
                    }
                else:
                    logger.error(f"Registration failed with status code: {response.status_code}")
                    return {'success': False, 'error': f'Registration failed with status code {response.status_code}'}
            else:
                logger.error(f"Registration failed with status code: {response.status_code}")
                return {'success': False, 'error': f'Registration failed with status code {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Unexpected error during registration: {e}", exc_info=True)
            return {'success': False, 'error': f'Unexpected error: {str(e)}'}
        
    def getPlayerId(self , telegram_username = None):
        try:
            
            
            # API endpoint
            getPlayersUrl = "https://agents.ichancy.com/global/api/Statistics/getPlayersStatisticsPro"

            # Prepare JSON payload
            payload = {               
                    "start": 0,
                    "limit": 10,
                    "filter": {}      
            }
            # Log the request details for debugging
            logger.info(f"Making request to: {getPlayersUrl}")
        
            # Submit registration
            logger.info("Submitting registration to API")
            try:
                response = self.session.post(
                    getPlayersUrl, 
                    json=payload, 
                    timeout=30
                )
                json = response.json()
                for row in json.get('result').get('records'):
                 if row['username'] == telegram_username:
                    return row['playerId']
                 
            except requests.exceptions.HTTPError as e:
                 logger.error(f"HTTP Error: {e}")
                 logger.error(f"Response status: {e.response.status_code}")
                
        except Exception as e:
                logger.error(f"Registration submission failed: {e}",exc_info=True)
                return {'success': False, 'error': f'Registration submission failed: {str(e)}'}

    def getAdminstratorBalance(self):
        try:
            
            
            # API endpoint
            getAgentWalletByAgentId = "https://agents.ichancy.com/global/api/Agent/getAgentWalletByAgentId"

            # Prepare JSON payload
            payload = {               
                   'affiliateId': config.ichancy.PARENT_ID,
                   'currencyCode': "NSP"

            }
            # Log the request details for debugging
            logger.info(f"Making request to: {getAgentWalletByAgentId}")
        
            # Submit registration
            logger.info("Submitting registration to API")
            try:
                response = self.session.post(
                    getAgentWalletByAgentId, 
                    json=payload, 
                    timeout=30
                )
                json = response.json()
                
                return int(json.get('result').get('balance'))
            except requests.exceptions.HTTPError as e:
                 logger.error(f"HTTP Error: {e}",exc_info=True)
                 logger.error(f"Response status: {e.response.status_code}")
                
        except Exception as e:
                logger.error(f"Registration submission failed: {e}",exc_info=True)
                return {'success': False, 'error': f'Registration submission failed: {str(e)}'}
        
    def getPlayerBalanceById(self , playerId):
        try:
            
            
            # API endpoint
            getPlayerBalanceById = "https://agents.ichancy.com/global/api/Player/getPlayerBalanceById"

            # Prepare JSON payload
            payload ={'playerId': playerId}

            # Log the request details for debugging
            logger.info(f"Making request to: {getPlayerBalanceById}")
        
            # Submit registration
            logger.info("Submitting registration to API")
            try:
                response = self.session.post(
                    getPlayerBalanceById, 
                    json=payload, 
                    timeout=30
                )
                print(playerId)
                json:list = response.json()
                balance = int(json.get('result')[0].get('balance'))
                return balance
            except requests.exceptions.HTTPError as e:
                 logger.error(f"HTTP Error: {e}",exc_info=True)
                 logger.error(f"Response status: {e.response.status_code}")
                
        except Exception as e:
                logger.error(f"Registration submission failed: {e}",exc_info=True)
                return {'success': False, 'error': f'Registration submission failed: {str(e)}'}

    def transfeerMoney(self , player_id = "321405978" , currencyCode = "NSP" , ammount = 1 , comment = None , moneyStatus = 5):
        try:
            
            
            # API endpoint
            getTransfeerUrl = "https://agents.ichancy.com/global/api/Player/depositToPlayer"

            # Prepare JSON payload
            payload = {'amount': ammount,
                      'comment': None,
                      'playerId': player_id, 
                      'currencyCode': currencyCode,
                      'moneyStatus': moneyStatus}

            # Log the request details for debugging
            logger.info(f"Making request to: {getTransfeerUrl}")
        
            # Submit registration
            logger.info("Submitting Transfeering money to API")
            try:
                response = self.session.post(
                    getTransfeerUrl, 
                    json=payload, 
                    timeout=30
                )

            
            except requests.exceptions.HTTPError as e:
                 logger.error(f"HTTP Error: {e}")
                 logger.error(f"Response status: {e.response.status_code}")
                
        except Exception as e:
                logger.error(f"Transfeer Money Failed: {e}",exc_info=True)
                return {'success': False, 'error': f'Transfeer Money failed: {str(e)}'}
        
    def WirhdrawMoney(self , player_id = "321405978" , currencyCode = "NSP" , ammount = 1 , comment = None , moneyStatus = 5):
        try:
            
            
            # API endpoint
            getWithdrawUrl = "https://agents.ichancy.com/global/api/Player/withdrawFromPlayer"

            # Prepare JSON payload
            payload = {'amount': -ammount,
                      'comment': None,
                      'playerId': player_id, 
                      'currencyCode': currencyCode,
                      'moneyStatus': moneyStatus}

            # Log the request details for debugging
            logger.info(f"Making request to: {getWithdrawUrl}")
        
            # Submit registration
            logger.info("Submitting Transfeering money to API")
            try:
                response = self.session.post(
                    getWithdrawUrl, 
                    json=payload, 
                    timeout=30
                )
            
            except requests.exceptions.HTTPError as e:
                 logger.error(f"HTTP Error: {e}")
                 logger.error(f"Response status: {e.response.status_code}")
                
        except Exception as e:
                logger.error(f"Transfeer Money Failed: {e}",exc_info=True)
                return {'success': False, 'error': f'Transfeer Money failed: {str(e)}'}
        
