import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from db_config import get_db_connection

st.set_page_config(page_title="SmartBank", layout="wide")

st.title("🏦 SmartBank System")

if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "active_menu" not in st.session_state:
    st.session_state.active_menu = "Register"


def show_api_response(response):
    """Display API response safely even when response is not JSON."""
    try:
        payload = response.json()
    except requests.exceptions.JSONDecodeError:
        payload = response.text.strip() or "No response body received from server."

    if response.ok:
        st.success(payload)
    else:
        st.error(f"Request failed ({response.status_code}): {payload}")

    return payload


def load_accounts(user_id=None):
    """Fetch account options for dropdown selectors."""
    conn = get_db_connection()
    if user_id:
        query = """
        SELECT a.account_id, a.account_type, a.balance, u.name
        FROM accounts a
        LEFT JOIN users u ON a.user_id = u.user_id
        WHERE a.user_id = %s
        ORDER BY a.account_id
        """
        df_accounts = pd.read_sql(query, conn, params=(user_id,))
    else:
        query = """
        SELECT a.account_id, a.account_type, a.balance, u.name
        FROM accounts a
        LEFT JOIN users u ON a.user_id = u.user_id
        ORDER BY a.account_id
        """
        df_accounts = pd.read_sql(query, conn)
    conn.close()
    return df_accounts

# Sidebar menu
menu_options = [
    "Register",
    "Login",
    "Create Account",
    "Deposit",
    "Withdraw",
    "Dashboard"
]

if st.session_state.active_menu not in menu_options:
    st.session_state.active_menu = "Register"

menu = st.sidebar.selectbox(
    "Menu",
    menu_options,
    index=menu_options.index(st.session_state.active_menu)
)
st.session_state.active_menu = menu

if st.session_state.user_id:
    st.sidebar.success(f"Logged in: {st.session_state.user_email}")
    if st.sidebar.button("Logout"):
        st.session_state.user_id = None
        st.session_state.user_email = None
        st.rerun()
else:
    st.sidebar.info("Please login to manage accounts.")

# ---------------- REGISTER ----------------
if menu == "Register":
    st.subheader("Register")

    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        res = requests.post("http://127.0.0.1:5000/register", json={
            "name": name,
            "email": email,
            "password": password
        })
        show_api_response(res)


# ---------------- LOGIN ----------------
elif menu == "Login":
    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = requests.post("http://127.0.0.1:5000/login", json={
            "email": email,
            "password": password
        })
        payload = show_api_response(res)
        if res.ok and isinstance(payload, dict) and payload.get("user_id"):
            st.session_state.user_id = payload["user_id"]
            st.session_state.user_email = email
            user_accounts = load_accounts(st.session_state.user_id)
            if user_accounts.empty:
                st.session_state.active_menu = "Create Account"
                st.rerun()


# ---------------- CREATE ACCOUNT ----------------
elif menu == "Create Account":
    st.subheader("Create Account")
    if not st.session_state.user_id:
        st.warning("Please login first to create an account.")
    else:
        account_type = st.selectbox("Account Type", ["savings", "current"])
        if st.button("Create Account"):
            res = requests.post("http://127.0.0.1:5000/create_account", json={
                "user_id": st.session_state.user_id,
                "account_type": account_type
            })
            show_api_response(res)


# ---------------- DEPOSIT ----------------
elif menu == "Deposit":
    st.subheader("Deposit")

    if not st.session_state.user_id:
        st.warning("Please login first to deposit.")
        st.stop()

    accounts_df = load_accounts(st.session_state.user_id)
    if accounts_df.empty:
        st.warning("No accounts found for your profile. Please create an account first.")
    else:
        options = accounts_df.to_dict("records")
        selected_account = st.selectbox(
            "Select Account",
            options=options,
            format_func=lambda a: (
                f"{a['account_id']} - {a['name']} ({a['account_type']}) | Balance: {a['balance']}"
            ),
        )
        amount = st.number_input("Amount", min_value=1.0, step=100.0)

        if st.button("Deposit"):
            res = requests.post("http://127.0.0.1:5000/deposit", json={
                "account_id": int(selected_account["account_id"]),
                "amount": float(amount)
            })
            show_api_response(res)


# ---------------- WITHDRAW ----------------
elif menu == "Withdraw":
    st.subheader("Withdraw")

    if not st.session_state.user_id:
        st.warning("Please login first to withdraw.")
        st.stop()

    accounts_df = load_accounts(st.session_state.user_id)
    if accounts_df.empty:
        st.warning("No accounts found for your profile. Please create an account first.")
    else:
        options = accounts_df.to_dict("records")
        selected_account = st.selectbox(
            "Select Account",
            options=options,
            format_func=lambda a: (
                f"{a['account_id']} - {a['name']} ({a['account_type']}) | Balance: {a['balance']}"
            ),
            key="withdraw_account",
        )
        amount = st.number_input("Amount", min_value=1.0, step=100.0, key="withdraw_amount")

        if st.button("Withdraw"):
            res = requests.post("http://127.0.0.1:5000/withdraw", json={
                "account_id": int(selected_account["account_id"]),
                "amount": float(amount)
            })
            show_api_response(res)


# ---------------- DASHBOARD ----------------
elif menu == "Dashboard":
    st.subheader("📊 Analytics Dashboard")

    if not st.session_state.user_id:
        st.warning("Please login first to view your dashboard.")
        st.stop()

    conn = get_db_connection()
    query = """
    SELECT t.*
    FROM transactions t
    JOIN accounts a ON t.account_id = a.account_id
    WHERE a.user_id = %s
    """
    df = pd.read_sql(query, conn, params=(st.session_state.user_id,))
    conn.close()

    if df.empty:
        st.warning("No transactions available yet")
    else:
        df['transaction_time'] = pd.to_datetime(df['transaction_time'])
        df['month'] = df['transaction_time'].dt.month

        st.dataframe(df)

        total_deposit = df[df['type'] == 'deposit']['amount'].sum()
        total_withdraw = df[df['type'] == 'withdraw']['amount'].sum()

        col1, col2 = st.columns(2)
        col1.metric("💰 Total Deposits", f"₹ {total_deposit}")
        col2.metric("💸 Total Withdrawals", f"₹ {total_withdraw}")

        summary = df.groupby(['month', 'type'])['amount'].sum().unstack().fillna(0)

        st.subheader("Monthly Summary")
        st.dataframe(summary)

        # Smaller chart
        fig, ax = plt.subplots(figsize=(6, 4))
        summary.plot(kind='bar', ax=ax)

        ax.set_title("Monthly Transactions")
        ax.set_xlabel("Month")
        ax.set_ylabel("Amount")

        plt.tight_layout()
        st.pyplot(fig)