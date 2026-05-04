import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import os
from db_config import get_db_connection

st.set_page_config(page_title="SmartBank", layout="wide")

st.title("🏦 SmartBank System")

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:5000").rstrip("/")

# Session
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# Sidebar
menu = st.sidebar.selectbox("Menu", ["Register", "Login", "Deposit", "Withdraw", "Dashboard"])

# Logout
if st.sidebar.button("Logout"):
    st.session_state.user_id = None

if st.session_state.user_id:
    st.sidebar.success(f"Logged in as User {st.session_state.user_id}")


def handle_response(res):
    try:
        data = res.json()
    except:
        st.error("Invalid server response")
        return

    if res.status_code in [200, 201]:
        st.success(data)
    else:
        st.error(data)


# Register
if menu == "Register":
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        res = requests.post(f"{API_BASE_URL}/register",
                            json={"name": name, "email": email, "password": password})
        handle_response(res)


# Login
elif menu == "Login":
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = requests.post(f"{API_BASE_URL}/login",
                            json={"email": email, "password": password})

        try:
            data = res.json()
            if "user_id" in data:
                st.session_state.user_id = data["user_id"]
                st.success("Login successful")
            else:
                st.error(data)
        except:
            st.error("Login failed")


# Fetch accounts
account_ids = []
if st.session_state.user_id:
    res = requests.get(f"{API_BASE_URL}/accounts/{st.session_state.user_id}")
    try:
        data = res.json()
        if data:
            df_accounts = pd.DataFrame(data)
            st.dataframe(df_accounts)
            account_ids = df_accounts["account_id"].tolist()
    except:
        pass


# Deposit
elif menu == "Deposit":
    if not st.session_state.user_id:
        st.warning("Login first")
    else:
        if account_ids:
            account_id = st.selectbox("Account", account_ids)
            amount = st.number_input("Amount")

            if st.button("Deposit"):
                res = requests.post(f"{API_BASE_URL}/deposit",
                                    json={"account_id": account_id, "amount": amount})
                handle_response(res)


# Withdraw
elif menu == "Withdraw":
    if not st.session_state.user_id:
        st.warning("Login first")
    else:
        if account_ids:
            account_id = st.selectbox("Account", account_ids)
            amount = st.number_input("Amount")

            if st.button("Withdraw"):
                res = requests.post(f"{API_BASE_URL}/withdraw",
                                    json={"account_id": account_id, "amount": amount})
                handle_response(res)


# Dashboard
elif menu == "Dashboard":
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM transactions", conn)

    if not df.empty:
        df['transaction_time'] = pd.to_datetime(df['transaction_time'])
        df['month'] = df['transaction_time'].dt.month

        summary = df.groupby(['month', 'type'])['amount'].sum().unstack().fillna(0)

        fig, ax = plt.subplots(figsize=(4, 2.5))
        summary.plot(kind='bar', ax=ax)
        st.pyplot(fig)