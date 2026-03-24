import mysql.connector
import config.database
from datetime import datetime
def initializeDatabase():

    try:
        mydb = getDatabaseConnection(initialize=True)
        cursor = mydb.cursor()
    

        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config.database.databaseName}")
        
        cursor.execute(f"USE {config.database.databaseName}")

        cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    telegram_id VARCHAR(25) UNIQUE NOT NULL,
                    telegram_username VARCHAR(255),
                    player_id VARCHAR(255) NOT NULL,
                    name VARCHAR(255),
                    password VARCHAR(255),
                    email VARCHAR(255) UNIQUE NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    balance INT DEFAULT 0,
                    account_balance INT DEFAULT 0 
                        )""")


        cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    provider_id INT,
                    provider_type VARCHAR(255),
                    user_id INT NOT NULL,
                    value INT NOT NULL,
                    action_type VARCHAR(255) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

        cursor.execute("""
                CREATE TABLE IF NOT EXISTS account_transactions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    status VARCHAR(255) NOT NULL,
                    action_type VARCHAR(255) NOT NULL,
                    value INT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)


        cursor.execute("""
                CREATE TABLE IF NOT EXISTS bemo_transactions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    transfer_num VARCHAR(255),
                    user_id INT NOT NULL,
                    status VARCHAR(255) NOT NULL,
                    action_type VARCHAR(255) NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    value INT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS syriatel_transactions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    transfer_num VARCHAR(255),
                    user_id INT NOT NULL,
                    status VARCHAR(255) NOT NULL,
                    action_type VARCHAR(255) NOT NULL,
                    value INT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS gifts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    telegram_goal_id VARCHAR(20) NOT NULL,
                    user_id INT NOT NULL,
                    redeemed_at DATETIME NULL,
                    code VARCHAR(25) NOT NULL,
                    ammount INT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages_to_admin (
                       id INT AUTO_INCREMENT PRIMARY KEY,
                       user_id INT NOT NULL,
                       message TEXT NOT NULL,
                       reply TEXT NULL,
                       created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
            """)

    except(Exception, mysql.connector.Error) as error: 
        print(f"Failed to connect to the database: {error}")


def getDatabaseConnection(initialize = False):
    try:
        if not initialize:
            mydb = mysql.connector.connect(
                host = config.database.host,
                port = config.database.port,
                username = config.database.username,
                password = config.database.password,
                database = config.database.databaseName
            )
            return mydb
        else:
            mydb = mysql.connector.connect(
            host = config.database.host,
            port = config.database.port,
            username = config.database.username,
            password = config.database.password,
            )
            return mydb
    except(Exception, mysql.connector.Error) as error: 
        print(f"Failed to connect to the database: {error}")

def getTelegramIdByUserId(userId):
    mydb = getDatabaseConnection()
    cursor = mydb.cursor()
    cursor.execute("SELECT telegram_id FROM users WHERE id = %s", (userId,))
    telegram_ids = cursor.fetchone()
    return telegram_ids[0] if telegram_ids else None

def getUserById(userId):
    mydb = getDatabaseConnection()
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (userId,))
    return cursor.fetchone()

def getUserByTelegramId(telegram_id):
    mydb = getDatabaseConnection()
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id,))
    return cursor.fetchone()

def getUserIdByTelegramId(telegram_id):
    mydb = getDatabaseConnection()
    cursor = mydb.cursor(dictionary=True)
    sql = """SELECT id FROM users WHERE telegram_id = %(telegram_id)s"""
    data = {
        'telegram_id' : telegram_id
    }
    cursor.execute(sql,data)
    return cursor.fetchone()

def insertGift(telegram_id , giftAmmount , telegram_goal_id , code):
    mydb = getDatabaseConnection()
    cursor = mydb.cursor()
    user = getUserByTelegramId(telegram_id)
    balance = user.get('balance') - int(giftAmmount)
    if balance < 0:
        mydb.close()
        return False
    sqlInsert = """
    UPDATE users SET balance = %(balance)s WHERE telegram_id = %(telegram_id)s
    """
    data = {
        'balance' : balance,
        'telegram_id':telegram_id
    }
    cursor.execute(sqlInsert, data)
    mydb.commit() 

    sqlInsert = """
                INSERT INTO gifts (telegram_goal_id , ammount , user_id , code) VALUES (%(telegram_goal_id)s, %(ammount)s , %(user_id)s , %(code)s)
            """
    data = {
            'telegram_goal_id' : telegram_goal_id ,
            'ammount' : giftAmmount,
            'user_id' : user.get('id'),
            'code' : code
        }
    cursor.execute(sqlInsert, data)
    mydb.commit()
    mydb.close()
    return True


def validateRedeemedAt(resault , cursor , mydb):
    gift_id = resault.get('id')
    sql = """
        UPDATE gifts SET redeemed_at = %(redeemed_at)s
        WHERE id = %(gift_id)s
        """
    data = {
    'gift_id': gift_id,
    'redeemed_at': datetime.now()
    }
    cursor.execute(sql,data)
    mydb.commit()


def addGiftAmmountToBalance(telegram_id , cursor , resault):
    sql = """SELECT balance FROM users WHERE telegram_id = %(telegram_id)s"""
    data = {
        'telegram_id':telegram_id,
    }
    cursor.execute(sql,data)
    newBalance = cursor.fetchone().get('balance')
    newBalance += resault.get('ammount')
    return newBalance

def insertTheNewBalance(telegram_id , cursor , resault , mydb):
    newBalance = addGiftAmmountToBalance(telegram_id , cursor , resault)
    sql = """
        UPDATE users SET balance = %(balance)s
        WHERE telegram_id = %(telegram_id)s
        """
    data = {
    'balance': newBalance,
    'telegram_id': telegram_id
    }
    cursor.execute(sql,data)
    mydb.commit()
    mydb.close()

    
def getGift(code , telegram_id):
     mydb = getDatabaseConnection()
     cursor = mydb.cursor(dictionary=True)
     sql = """SELECT * FROM users U JOIN gifts G WHERE G.user_id = U.id 
     AND G.telegram_goal_id = %(telegram_id)s AND code = %(code)s
     AND redeemed_at IS NULL"""
     data = {
         'telegram_id':telegram_id,
         'code':code
     }     
     cursor.execute(sql,data)
     resault = cursor.fetchone()
     if resault:
         validateRedeemedAt(resault , cursor , mydb)
         insertTheNewBalance(telegram_id , cursor , resault , mydb)
         return True
     return False
    
def insertNewUser(telegram_id, telegram_username = None):

    mydb = getDatabaseConnection()
    cursor = mydb.cursor()
    
    if not getUserByTelegramId(telegram_id):
        sqlInsert = """
                INSERT INTO users (telegram_id , telegram_username) VALUES (%(telegram_id)s, %(telegram_username)s)
            """
        data = {
            'telegram_id' : telegram_id,
            'telegram_username' : telegram_username 
        }
        cursor.execute(sqlInsert, data)
        mydb.commit()
    
    mydb.close()

def insertUserDetailes(telegram_id,name,password,email,player_id):

    mydb = getDatabaseConnection()

    cursor = mydb.cursor()    
    
    sqlInsert = """
    UPDATE users SET name = %(name)s, password = %(password)s, email = %(email)s , player_id = %(player_id)s
    WHERE telegram_id = %(telegram_id)s
    """

    data = {
        'name': name,
        'password': password,
        'email': email,
        'telegram_id': telegram_id,
        'player_id': player_id
    }
    cursor.execute(sqlInsert, data)
    mydb.commit()
    mydb.close()   

def insertMessageToAdmin(telegram_id,message):
    mydb = getDatabaseConnection()
    cursor = mydb.cursor()
    user_id = getUserIdByTelegramId(telegram_id).get('id')
    sql = """INSERT INTO messages_to_admin (user_id , message) VALUES (%(user_id)s , %(message)s)  """
    data = {
        'user_id': user_id,
        'message': message
    }
    cursor.execute(sql,data)
    mydb.commit()
    mydb.close()

def insertNewBalance(telegram_id ,newBalance ):
    mydb = getDatabaseConnection()
    cursor = mydb.cursor()
    sql = """
        UPDATE users SET balance = %(balance)s
        WHERE telegram_id = %(telegram_id)s
        """
    data = {
    'balance': newBalance,
    'telegram_id': telegram_id
    }
    cursor.execute(sql,data)
    mydb.commit()
    mydb.close()

def insertNewAccountBalance(telegram_id ,newBalance ):
    mydb = getDatabaseConnection()
    cursor = mydb.cursor()
    sql = """
        UPDATE users SET account_balance = %(account_balance)s
        WHERE telegram_id = %(telegram_id)s
        """
    data = {
    'account_balance': newBalance,
    'telegram_id': telegram_id
    }
    cursor.execute(sql,data)
    mydb.commit()
    mydb.close()

def insertMessageToAdmin(telegram_id,message):
    mydb = getDatabaseConnection()
    cursor = mydb.cursor()
    user_id = getUserIdByTelegramId(telegram_id).get('id')
    sql = """INSERT INTO messages_to_admin (user_id , message) VALUES (%(user_id)s , %(message)s)  """
    data = {
        'user_id': user_id,
        'message': message
    }
    cursor.execute(sql,data)
    mydb.commit()
    mydb.close()

def insertNewBalance(telegram_id ,newBalance ):
    mydb = getDatabaseConnection()
    cursor = mydb.cursor()
    sql = """
        UPDATE users SET balance = %(balance)s
        WHERE telegram_id = %(telegram_id)s
        """
    data = {
    'balance': newBalance,
    'telegram_id': telegram_id
    }
    cursor.execute(sql,data)
    mydb.commit()
    mydb.close()

# Transaction management functions
def insertTransaction(telegram_id, value, action_type, provider_type=None, transfer_num=None):
    """Insert a new transaction into the database"""
    mydb = getDatabaseConnection()
    cursor = mydb.cursor(dictionary=True)
    
    user = getUserByTelegramId(telegram_id)
    user_id = user['id'] if user else None

    if not user_id:
        mydb.close()
        return None

    # Determine which table to use based on provider type
    if provider_type == 'syriatel':
        sqlInsert = """
            INSERT INTO syriatel_transactions (user_id, transfer_num, value, status, action_type) 
            VALUES (%(user_id)s, %(transfer_num)s, %(value)s, %(status)s, %(action_type)s)
        """
        data = {
            'user_id': user_id,
            'transfer_num': transfer_num,
            'value': value,
            'status': 'pending',
            'action_type': action_type
        }
    elif provider_type == 'bemo':
        sqlInsert = """
            INSERT INTO bemo_transactions (user_id, transfer_num, value, status, action_type) 
            VALUES (%(user_id)s, %(transfer_num)s, %(value)s, %(status)s, %(action_type)s)
        """
        data = {
            'user_id': user_id,
            'transfer_num': transfer_num,
            'value': value,
            'status': 'pending',
            'action_type': action_type
        }
    
    cursor.execute(sqlInsert, data)
    provider_id = cursor.lastrowid
    
    # Use general transactions table
    sqlInsert = """
        INSERT INTO transactions (user_id, provider_id, provider_type, value, action_type) 
        VALUES (%(user_id)s, %(provider_id)s, %(provider_type)s, %(value)s, %(action_type)s)
    """
    data = {
        'user_id': user_id,
        'provider_id': provider_id,
        'provider_type': provider_type,
        'value': value,
        'action_type': action_type
    }

    cursor.execute(sqlInsert, data)
    
    mydb.commit()
    mydb.close()
    
    return provider_id

def get_transaction_table_name_by_type(transaction_type):
    match(transaction_type):
        case 'syriatel':
            return 'syriatel_transactions';
        case 'bemo':
            return 'bemo_transactions';
        case _:
            return None

def get_transaction_by_id(transaction_id, transaction_type):
    """Get transaction by ID from any transaction table"""
    mydb = getDatabaseConnection()
    cursor = mydb.cursor(dictionary=True)

    table = get_transaction_table_name_by_type(transaction_type)
    
    if not table:
        raise ValueError("Please provide a valid transaction type")

    cursor.execute(f"SELECT * FROM {table} WHERE id = %s", (transaction_id,))
    result = cursor.fetchone()

    mydb.close()
    return result

def get_pending_transactions():
    """Get all pending transactions from all transaction tables"""
    mydb = getDatabaseConnection()
    cursor = mydb.cursor(dictionary=True)
    
    # Get pending transactions from all tables
    all_transactions = []
    
    tables = [
        ('transactions', 'provider_type'),
        ('syriatel_transactions', 'transfer_num'),
        ('bemo_transactions', 'transfer_num'),
        ('account_transactions', 'action_type')
    ]
    
    for table, extra_field in tables:
        try:
            cursor.execute(f"SELECT * FROM {table} WHERE status = 'pending' ORDER BY created_at DESC")
            results = cursor.fetchall()
            for result in results:
                result['table_name'] = table
                all_transactions.append(result)
        except:
            continue
    
    mydb.close()
    return sorted(all_transactions, key=lambda x: x['created_at'], reverse=True)

def update_transaction_status(transaction_id, transaction_type, status):
    """Update transaction status in the appropriate table"""
    mydb = getDatabaseConnection()
    cursor = mydb.cursor()
     
    table = get_transaction_table_name_by_type(transaction_type)
    
    if not table:
        raise ValueError("Please provide a valid transaction type")

    cursor.execute(f"UPDATE {table} SET status = %s WHERE id = %s", (status, transaction_id))

    if cursor.rowcount > 0:
        mydb.commit()
        mydb.close()
        return True

    mydb.close()
    return False

def update_user_balance(user_id, amount):
    """Update user balance (add amount to current balance)"""
    mydb = getDatabaseConnection()
    cursor = mydb.cursor()
    
    try:
        cursor.execute("UPDATE users SET balance = %s WHERE id = %s", (amount, user_id))
        mydb.commit()
        mydb.close()
        return True
    except Exception as e:
        print(f"Error updating user balance: {e}")
        mydb.close()
        return False

def update_user_account_balance(user_id, amount):
    """Update user balance (add amount to current balance)"""
    mydb = getDatabaseConnection()
    cursor = mydb.cursor()
    
    try:
        cursor.execute("UPDATE users SET account_balance = %s WHERE id = %s", (amount, user_id))
        mydb.commit()
        mydb.close()
        return True
    except Exception as e:
        print(f"Error updating user balance: {e}")
        mydb.close()
        return False

def get_user_balance(user_id):
    """Get user current balance"""
    mydb = getDatabaseConnection()
    cursor = mydb.cursor()
    
    try:
        cursor.execute("SELECT balance FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        mydb.close()
        return result[0] if result else 0
    except Exception as e:
        print(f"Error getting user balance: {e}")
        mydb.close()
        return 0


def insertInTransactionAccount(user_id , status , action_type , value):
    mydb = getDatabaseConnection()
    cursor = mydb.cursor(dictionary=True)
    sql = """INSERT INTO account_transactions (user_id , status , action_type , value) VALUES (%(user_id)s , %(status)s , %(action_type)s , %(value)s)"""
    data = {
        'user_id': user_id,
        'status' : status,
        'action_type': action_type,
        'value':value
    }
    cursor.execute(sql,data)
    mydb.commit()
    mydb.close()














initializeDatabase()
