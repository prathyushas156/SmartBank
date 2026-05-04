import os
import mysql.connector


def _get_setting(key, default=None):
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)


def get_db_connection():
    """
    Supports both local MySQL and GCP Cloud SQL.
    - Local: use DB_HOST/DB_USER/DB_PASSWORD/DB_NAME
    - Cloud SQL on Cloud Run: set INSTANCE_CONNECTION_NAME
    """
    config = {
        "user": _get_setting("DB_USER", "root"),
        "password": _get_setting("DB_PASSWORD", ""),
        "database": _get_setting("DB_NAME", "smartbank"),
    }

    instance_connection_name = _get_setting("INSTANCE_CONNECTION_NAME")
    if instance_connection_name:
        # Cloud SQL Unix socket path for Cloud Run.
        config["unix_socket"] = f"/cloudsql/{instance_connection_name}"
    else:
        config["host"] = _get_setting("DB_HOST", "127.0.0.1")
        config["port"] = int(_get_setting("DB_PORT", "3306"))

    return mysql.connector.connect(**config)