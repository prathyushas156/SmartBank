from db_config import get_db_connection

def create_account(user_id, account_type):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "INSERT INTO accounts (user_id, account_type) VALUES (%s, %s)"
    cursor.execute(query, (user_id, account_type))

    conn.commit()
    cursor.close()
    conn.close()


def get_balance(account_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT balance FROM accounts WHERE account_id=%s", (account_id,))
    balance = cursor.fetchone()[0]

    cursor.close()
    conn.close()
    return balance


def update_balance(account_id, new_balance):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE accounts SET balance=%s WHERE account_id=%s",
                   (new_balance, account_id))

    conn.commit()
    cursor.close()
    conn.close()