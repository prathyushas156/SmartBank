import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import os
from db_config import get_db_connection

st.set_page_config(page_title="SmartBank", layout="wide")

st.title("🏦 SmartBank System")

def get_api_base_url():
    # Streamlit Cloud secrets take priority.
    if "API_BASE_URL" in st.secrets:
        return str(st.secrets["API_BASE_URL"]).rstrip("/")
    # Local env fallback.
    return os.getenv("API_BASE_URL", "http://127.0.0.1:5000").rstrip("/")


API_BASE_URL = get_api_base_url()

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


def safe_request(method, endpoint, **kwargs):
    url = f"{API_BASE_URL}{endpoint}"
    try:
        return requests.request(method, url, timeout=15, **kwargs)
    except requests.exceptions.ConnectionError:
        st.error(
            f"Cannot connect to backend API at {API_BASE_URL}. "
            "Please verify API_BASE_URL in Streamlit secrets and confirm your Flask API is deployed/running."
        )
    except requests.exceptions.Timeout:
        st.error("Backend API request timed out. Please try again in a few seconds.")
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
    return None


# Register
if menu == "Register":
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        res = safe_request(
            "POST",
            "/register",
            json={"name": name, "email": email, "password": password}
        )
        if res is not None:
            handle_response(res)


# Login
elif menu == "Login":
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = safe_request(
            "POST",
            "/login",
            json={"email": email, "password": password}
        )
        if res is None:
            st.stop()

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
    res = safe_request("GET", f"/accounts/{st.session_state.user_id}")
    if res is not None:
        try:
            data = res.json()
            if data:
                df_accounts = pd.DataFrame(data)
                st.dataframe(df_accounts)
                account_ids = df_accounts["account_id"].tolist()
        except Exception:
            st.error("Could not parse accounts response from backend.")


# Deposit
elif menu == "Deposit":
    if not st.session_state.user_id:
        st.warning("Login first")
    else:
        if account_ids:
            account_id = st.selectbox("Account", account_ids)
            amount = st.number_input("Amount")

            if st.button("Deposit"):
                res = safe_request(
                    "POST",
                    "/deposit",
                    json={"account_id": account_id, "amount": amount}
                )
                if res is not None:
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
                res = safe_request(
                    "POST",
                    "/withdraw",
                    json={"account_id": account_id, "amount": amount}
                )
                if res is not None:
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