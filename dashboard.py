import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from decimal import Decimal
from db_config import get_db_connection
from models.user_model import create_user, login_user
from models.account_model import create_account, get_accounts
from services.banking_service import deposit, withdraw

st.set_page_config(page_title="SmartBank", layout="wide")
st.title("🏦 SmartBank System")

if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "active_menu" not in st.session_state:
    st.session_state.active_menu = "Register"

menu_options = ["Register", "Login", "Create Account", "Deposit", "Withdraw", "Dashboard"]
if st.session_state.active_menu not in menu_options:
    st.session_state.active_menu = "Register"

menu = st.sidebar.selectbox("Menu", menu_options, index=menu_options.index(st.session_state.active_menu))
st.session_state.active_menu = menu

if st.session_state.user_id:
    st.sidebar.success(f"Logged in as {st.session_state.user_name}")
    if st.sidebar.button("Logout"):
        st.session_state.user_id = None
        st.session_state.user_name = None
        st.session_state.active_menu = "Login"
        st.rerun()
else:
    st.sidebar.info("Please login to continue.")


def load_my_accounts():
    if not st.session_state.user_id:
        return pd.DataFrame()
    data = get_accounts(st.session_state.user_id)
    return pd.DataFrame(data) if data else pd.DataFrame()


if menu == "Register":
    st.subheader("Register")
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        if not name or not email or not password:
            st.warning("All fields are required.")
        elif create_user(name, email, password):
            st.success("User registered successfully. Please login.")
            st.session_state.active_menu = "Login"
            st.rerun()
        else:
            st.error("Registration failed. Email may already exist.")

elif menu == "Login":
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login_user(email, password)
        if user:
            st.session_state.user_id = user["user_id"]
            st.session_state.user_name = user["name"]
            st.success("Login successful.")

            my_accounts = load_my_accounts()
            st.session_state.active_menu = "Create Account" if my_accounts.empty else "Deposit"
            st.rerun()
        else:
            st.error("Invalid credentials.")

elif menu == "Create Account":
    st.subheader("Create Account")
    if not st.session_state.user_id:
        st.warning("Please login first.")
    else:
        account_type = st.selectbox("Account Type", ["savings", "current"])
        if st.button("Create Account"):
            account_id = create_account(st.session_state.user_id, account_type)
            st.success(f"Account created successfully. Account ID: {account_id}")
            st.session_state.active_menu = "Deposit"
            st.rerun()

elif menu == "Deposit":
    st.subheader("Deposit")
    if not st.session_state.user_id:
        st.warning("Please login first.")
    else:
        accounts_df = load_my_accounts()
        if accounts_df.empty:
            st.info("No accounts found. Create one first.")
            if st.button("Go to Create Account"):
                st.session_state.active_menu = "Create Account"
                st.rerun()
        else:
            options = accounts_df.to_dict("records")
            selected_account = st.selectbox(
                "Select Account",
                options=options,
                format_func=lambda a: f"{a['account_id']} - {a['account_type']} | Balance: {a['balance']}"
            )
            amount = st.number_input("Amount", min_value=1.0, step=100.0)

            if st.button("Deposit"):
                try:
                    new_balance = deposit(int(selected_account["account_id"]), Decimal(str(amount)))
                    st.success(f"Deposit successful. New balance: {new_balance}")
                except ValueError as e:
                    st.error(str(e))
                except Exception:
                    st.error("Deposit failed. Please try again.")

elif menu == "Withdraw":
    st.subheader("Withdraw")
    if not st.session_state.user_id:
        st.warning("Please login first.")
    else:
        accounts_df = load_my_accounts()
        if accounts_df.empty:
            st.info("No accounts found. Create one first.")
            if st.button("Go to Create Account", key="withdraw_go_create"):
                st.session_state.active_menu = "Create Account"
                st.rerun()
        else:
            options = accounts_df.to_dict("records")
            selected_account = st.selectbox(
                "Select Account",
                options=options,
                format_func=lambda a: f"{a['account_id']} - {a['account_type']} | Balance: {a['balance']}",
                key="withdraw_account"
            )
            amount = st.number_input("Amount", min_value=1.0, step=100.0, key="withdraw_amount")

            if st.button("Withdraw"):
                try:
                    new_balance = withdraw(int(selected_account["account_id"]), Decimal(str(amount)))
                    if new_balance is None:
                        st.error("Insufficient balance.")
                    else:
                        st.success(f"Withdraw successful. New balance: {new_balance}")
                except ValueError as e:
                    st.error(str(e))
                except Exception:
                    st.error("Withdraw failed. Please try again.")

elif menu == "Dashboard":
    st.subheader("Dashboard")
    if not st.session_state.user_id:
        st.warning("Please login first.")
    else:
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
            st.info("No transactions available yet.")
        else:
            df["transaction_time"] = pd.to_datetime(df["transaction_time"])
            df["month"] = df["transaction_time"].dt.month
            st.dataframe(df)

            total_deposit = df[df["type"] == "deposit"]["amount"].sum()
            total_withdraw = df[df["type"] == "withdraw"]["amount"].sum()

            col1, col2 = st.columns(2)
            col1.metric("Total Deposits", f"{total_deposit}")
            col2.metric("Total Withdrawals", f"{total_withdraw}")

            summary = df.groupby(["month", "type"])["amount"].sum().unstack().fillna(0)
            fig, ax = plt.subplots(figsize=(6, 4))
            summary.plot(kind="bar", ax=ax)
            ax.set_title("Monthly Transactions")
            ax.set_xlabel("Month")
            ax.set_ylabel("Amount")
            plt.tight_layout()
            st.pyplot(fig)