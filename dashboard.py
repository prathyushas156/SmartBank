import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

st.set_page_config(page_title="SmartBank", layout="wide")
st.title("🏦 SmartBank System")

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:5000").rstrip("/")

if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "active_menu" not in st.session_state:
    st.session_state.active_menu = "Register"

menu_options = ["Register", "Login", "Create Account", "Deposit", "Withdraw", "Dashboard"]
if st.session_state.active_menu not in menu_options:
    st.session_state.active_menu = "Register"

menu = st.sidebar.selectbox("Menu", menu_options, index=menu_options.index(st.session_state.active_menu))
st.session_state.active_menu = menu

st.sidebar.caption(f"API: {API_BASE_URL}")

if st.session_state.user_id:
    st.sidebar.success(f"Logged in: {st.session_state.user_email}")
    if st.sidebar.button("Logout"):
        st.session_state.user_id = None
        st.session_state.user_email = None
        st.session_state.active_menu = "Login"
        st.rerun()
else:
    st.sidebar.info("Please login to continue.")


def safe_request(method, path, **kwargs):
    try:
        return requests.request(method, f"{API_BASE_URL}{path}", timeout=15, **kwargs)
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return None


def show_api_result(res):
    if res is None:
        return None
    try:
        payload = res.json()
    except Exception:
        payload = res.text
    if res.ok:
        st.success(payload)
    else:
        st.error(payload)
    return payload


def load_accounts_df():
    if not st.session_state.user_id:
        return pd.DataFrame()
    res = safe_request("GET", f"/accounts/{st.session_state.user_id}")
    if res is None or not res.ok:
        show_api_result(res)
        return pd.DataFrame()
    data = res.json()
    return pd.DataFrame(data) if data else pd.DataFrame()


if menu == "Register":
    st.subheader("Register")
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        res = safe_request("POST", "/register", json={"name": name, "email": email, "password": password})
        payload = show_api_result(res)
        if res is not None and res.ok:
            st.session_state.active_menu = "Login"
            st.rerun()

elif menu == "Login":
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = safe_request("POST", "/login", json={"email": email, "password": password})
        payload = show_api_result(res)
        if res is not None and res.ok and isinstance(payload, dict) and payload.get("user_id"):
            st.session_state.user_id = payload["user_id"]
            st.session_state.user_email = email
            accounts_df = load_accounts_df()
            st.session_state.active_menu = "Create Account" if accounts_df.empty else "Deposit"
            st.rerun()

elif menu == "Create Account":
    st.subheader("Create Account")
    if not st.session_state.user_id:
        st.warning("Please login first.")
    else:
        account_type = st.selectbox("Account Type", ["savings", "current"])
        if st.button("Create Account"):
            res = safe_request(
                "POST",
                "/create_account",
                json={"user_id": st.session_state.user_id, "account_type": account_type},
            )
            show_api_result(res)

elif menu == "Deposit":
    st.subheader("Deposit")
    if not st.session_state.user_id:
        st.warning("Please login first.")
    else:
        accounts_df = load_accounts_df()
        if accounts_df.empty:
            st.info("No accounts found. Create one first.")
        else:
            options = accounts_df.to_dict("records")
            selected = st.selectbox(
                "Select Account",
                options=options,
                format_func=lambda a: f"{a['account_id']} - {a.get('account_type','')} | Balance: {a.get('balance', 0)}",
            )
            amount = st.number_input("Amount", min_value=1.0, step=100.0)
            if st.button("Deposit"):
                res = safe_request(
                    "POST",
                    "/deposit",
                    json={"account_id": int(selected["account_id"]), "amount": float(amount)},
                )
                show_api_result(res)

elif menu == "Withdraw":
    st.subheader("Withdraw")
    if not st.session_state.user_id:
        st.warning("Please login first.")
    else:
        accounts_df = load_accounts_df()
        if accounts_df.empty:
            st.info("No accounts found. Create one first.")
        else:
            options = accounts_df.to_dict("records")
            selected = st.selectbox(
                "Select Account",
                options=options,
                format_func=lambda a: f"{a['account_id']} - {a.get('account_type','')} | Balance: {a.get('balance', 0)}",
                key="withdraw_account",
            )
            amount = st.number_input("Amount", min_value=1.0, step=100.0, key="withdraw_amount")
            if st.button("Withdraw"):
                res = safe_request(
                    "POST",
                    "/withdraw",
                    json={"account_id": int(selected["account_id"]), "amount": float(amount)},
                )
                show_api_result(res)

elif menu == "Dashboard":
    st.subheader("📊 Analytics Dashboard")
    if not st.session_state.user_id:
        st.warning("Please login first.")
    else:
        accounts_df = load_accounts_df()
        if accounts_df.empty:
            st.info("No accounts found.")
        else:
            account_id = int(accounts_df.iloc[0]["account_id"])
            res = safe_request("GET", f"/transactions/{account_id}")
            if res is None or not res.ok:
                show_api_result(res)
            else:
                df = pd.DataFrame(res.json())
                if df.empty:
                    st.info("No transactions available yet.")
                else:
                    df["transaction_time"] = pd.to_datetime(df["transaction_time"])
                    df["month"] = df["transaction_time"].dt.month
                    # Ensure numeric amounts for analytics/plots (API may return strings)
                    df["amount"] = pd.to_numeric(df.get("amount"), errors="coerce")
                    st.dataframe(df)

                    total_deposit = df[df["type"] == "deposit"]["amount"].sum(min_count=1)
                    total_withdraw = df[df["type"] == "withdraw"]["amount"].sum(min_count=1)

                    col1, col2 = st.columns(2)
                    col1.metric("Total Deposits", f"{0 if pd.isna(total_deposit) else total_deposit:.2f}")
                    col2.metric("Total Withdrawals", f"{0 if pd.isna(total_withdraw) else total_withdraw:.2f}")

                    summary = (
                        df.dropna(subset=["amount"])
                        .groupby(["month", "type"])["amount"]
                        .sum()
                        .unstack()
                        .fillna(0)
                    )

                    if summary.empty:
                        st.info("No numeric transaction amounts available to plot yet.")
                    else:
                        fig, ax = plt.subplots(figsize=(6, 4))
                        summary.plot(kind="bar", ax=ax)
                        ax.set_title("Monthly Transactions")
                        ax.set_xlabel("Month")
                        ax.set_ylabel("Amount")
                        plt.tight_layout()
                        st.pyplot(fig)