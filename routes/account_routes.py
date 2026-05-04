from flask import Blueprint, jsonify, request
from models.account_model import get_accounts, create_account

account_bp = Blueprint('account', __name__)


@account_bp.route('/accounts/<int:user_id>', methods=['GET'])
def fetch_accounts(user_id):
    return jsonify(get_accounts(user_id))


@account_bp.route('/create_account', methods=['POST'])
def create_acc():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    account_type = data.get("account_type", "savings")

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    account_id = create_account(user_id, account_type)
    return jsonify({"message": "Account created", "account_id": account_id}), 201