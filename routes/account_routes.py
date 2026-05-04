from flask import Blueprint, request, jsonify
from models.account_model import create_account

account_bp = Blueprint('account', __name__)

@account_bp.route('/create_account', methods=['POST'])
def create_acc():
    data = request.json
    create_account(data['user_id'], data['account_type'])
    return jsonify({"message": "Account created"})