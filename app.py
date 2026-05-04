from flask import Flask
from routes.auth_routes import auth_bp
from routes.account_routes import account_bp
from routes.transaction_routes import txn_bp
import os

app = Flask(__name__)

app.register_blueprint(auth_bp)
app.register_blueprint(account_bp)
app.register_blueprint(txn_bp)


@app.route('/')
def home():
    return "SmartBank API Running 🚀"


if __name__ == '__main__':
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)