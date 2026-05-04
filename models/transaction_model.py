from db_config import get_db_connection

def add_transaction(account_id, txn_type, amount, balance_after):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO transactions (account_id, type, amount, balance_after)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (account_id, txn_type, amount, balance_after))

    conn.commit()
    cursor.close()
    conn.close()


def get_transactions(account_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM transactions WHERE account_id=%s", (account_id,))
    data = cursor.fetchall()

    cursor.close()
    conn.close()
    return data