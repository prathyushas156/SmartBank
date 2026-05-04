import os
import mysql.connector


def get_db_connection():
    """
    Supports both local MySQL and GCP Cloud SQL.
    - Local: use DB_HOST/DB_USER/DB_PASSWORD/DB_NAME
    - Cloud SQL on Cloud Run: set INSTANCE_CONNECTION_NAME
    """
    config = {
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "smartbank"),
    }

    instance_connection_name = os.getenv("INSTANCE_CONNECTION_NAME")
    if instance_connection_name:
        # Cloud SQL Unix socket path for Cloud Run.
        config["unix_socket"] = f"/cloudsql/{instance_connection_name}"
    else:
        config["host"] = os.getenv("DB_HOST", "127.0.0.1")
        config["port"] = int(os.getenv("DB_PORT", "3306"))

    return mysql.connector.connect(**config)