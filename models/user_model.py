from db_config import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash


def create_user(name, email, password):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        hashed_password = generate_password_hash(password)

        query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
        cursor.execute(query, (name, email, hashed_password))

        conn.commit()
        return True

    except Exception as e:
        print("Create User Error:", e)
        return False

    finally:
        cursor.close()
        conn.close()


def login_user(email, password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            return user
        return None

    finally:
        cursor.close()
        conn.close()