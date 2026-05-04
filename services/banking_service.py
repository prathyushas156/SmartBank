from models.account_model import get_balance, update_balance
from models.transaction_model import add_transaction
from decimal import Decimal, InvalidOperation


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