from flask import Blueprint, request, jsonify
from services.banking_service import deposit, withdraw
from models.transaction_model import get_transactions

txn_bp = Blueprint('transaction', __name__)

@txn_bp.route('/deposit', methods=['POST'])
def deposit_route():
    try:
        data = request.get_json() or {}
        balance = deposit(data['account_id'], data['amount'])
        return jsonify({"balance": float(balance)})
    except KeyError:
        return jsonify({"error": "account_id and amount are required"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "Server error"}), 500


@txn_bp.route('/withdraw', methods=['POST'])
def withdraw_route():
    try:
        data = request.get_json() or {}
        balance = withdraw(data['account_id'], data['amount'])

        if balance is None:
            return jsonify({"error": "Insufficient balance"}), 400

        return jsonify({"balance": float(balance)})
    except KeyError:
        return jsonify({"error": "account_id and amount are required"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "Server error"}), 500


@txn_bp.route('/transactions/<int:account_id>', methods=['GET'])
def transactions(account_id):
    return jsonify(get_transactions(account_id))