from flask import Flask
from routes.auth_routes import auth_bp
from routes.account_routes import account_bp
from routes.transaction_routes import txn_bp

app = Flask(__name__)

# ✅ ADD THIS ROUTE
@app.route('/')
def home():
    return "SmartBank API is running 🚀"

# ✅ REGISTER BLUEPRINTS
app.register_blueprint(auth_bp)
app.register_blueprint(account_bp)
app.register_blueprint(txn_bp)

if __name__ == '__main__':
    app.run(debug=True)