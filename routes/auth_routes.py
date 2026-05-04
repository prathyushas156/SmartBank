from flask import Blueprint, request, jsonify
from models.user_model import create_user, login_user
import mysql.connector

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not name or not email or not password:
            return jsonify({"error": "All fields required"}), 400

        success = create_user(name, email, password)

        if success:
            return jsonify({"message": "User registered"}), 201
        else:
            return jsonify({"error": "Email exists"}), 400

    except Exception as e:
        print(e)
        if isinstance(e, mysql.connector.Error):
            return jsonify({"error": f"Database error: {e}"}), 500
        return jsonify({"error": f"Server error: {type(e).__name__}"}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        email = data.get('email')
        password = data.get('password')

        user = login_user(email, password)

        if user:
            return jsonify({
                "message": "Login successful",
                "user_id": user['user_id']
            })
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        print(e)
        if isinstance(e, mysql.connector.Error):
            return jsonify({"error": f"Database error: {e}"}), 500
        return jsonify({"error": f"Server error: {type(e).__name__}"}), 500