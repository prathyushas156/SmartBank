from flask import Blueprint, request, jsonify
from services.banking_service import deposit, withdraw
from models.transaction_model import get_transactions

txn_bp = Blueprint('transaction', __name__)


@txn_bp.route('/deposit', methods=['POST'])
def deposit_route():
    try:
        data = request.get_json()

        account_id = data.get('account_id')
        amount = data.get('amount')

        if not account_id or not amount:
            return jsonify({"error": "Missing fields"}), 400

        balance = deposit(account_id, amount)

        return jsonify({
            "message": "Deposit successful",
            "balance": float(balance)
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print("Deposit Error:", e)
        return jsonify({"error": "Server error"}), 500


@txn_bp.route('/withdraw', methods=['POST'])
def withdraw_route():
    try:
        data = request.get_json()

        account_id = data.get('account_id')
        amount = data.get('amount')

        balance = withdraw(account_id, amount)

        if balance is None:
            return jsonify({"error": "Insufficient balance"}), 400

        return jsonify({
            "message": "Withdraw successful",
            "balance": float(balance)
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print("Withdraw Error:", e)
        return jsonify({"error": "Server error"}), 500


@txn_bp.route('/transactions/<int:account_id>', methods=['GET'])
def transactions(account_id):
    return jsonify(get_transactions(account_id))