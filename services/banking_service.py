from models.transaction_model import add_transaction
from db_config import get_db_connection
from decimal import Decimal, InvalidOperation


def get_balance(account_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT balance FROM accounts WHERE account_id=%s", (account_id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result[0] if result else 0


def update_balance(account_id, new_balance):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE accounts SET balance=%s WHERE account_id=%s",
                   (new_balance, account_id))

    conn.commit()
    cursor.close()
    conn.close()


def deposit(account_id, amount):
    try:
        amount = Decimal(str(amount))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("Invalid amount")

    if amount <= 0:
        raise ValueError("Amount must be greater than zero")

    balance = get_balance(account_id)
    new_balance = balance + amount

    update_balance(account_id, new_balance)
    add_transaction(account_id, "deposit", amount, new_balance)

    return new_balance


def withdraw(account_id, amount):
    try:
        amount = Decimal(str(amount))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("Invalid amount")

    if amount <= 0:
        raise ValueError("Amount must be greater than zero")

    balance = get_balance(account_id)

    if balance < amount:
        return None

    new_balance = balance - amount

    update_balance(account_id, new_balance)
    add_transaction(account_id, "withdraw", amount, new_balance)

    return new_balance