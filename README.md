# SmartBank

SmartBank is a Python banking application with:

- User registration and login
- Account creation (Savings / Current)
- Deposit and withdraw operations
- Transaction history and analytics dashboard (Streamlit)
- MySQL backend

## Tech Stack

- Python
- Flask (API)
- Streamlit (UI Dashboard)
- MySQL
- Pandas + Matplotlib

## Project Structure

- `app.py` - Flask API entrypoint
- `dashboard.py` - Streamlit dashboard (UI)
- `db_config.py` - Database connection helper
- `routes/` - API routes
- `services/` - Business logic
- `models/` - Database operations

## Prerequisites

- Python 3.10+
- MySQL running locally
- A MySQL database named `smartbank`

## Setup (Local)

### 1) Clone

```bash
git clone https://github.com/prathyushas156/SmartBank.git
cd SmartBank
```

### 2) Create a virtual environment and install dependencies (Windows PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3) Configure database environment variables (Windows PowerShell)

Set these **in the terminal session** where you run the API:

```powershell
$env:DB_HOST="localhost"
$env:DB_PORT="3306"
$env:DB_USER="root"
$env:DB_PASSWORD="YOUR_MYSQL_PASSWORD"
$env:DB_NAME="smartbank"
```

## Run (2 Terminals)

This project runs as:
- **Flask API** (`app.py`) on port `5000`
- **Streamlit UI** (`dashboard.py`) on port `8501`

### Terminal 1: Start the Flask API

```powershell
cd D:\smartbank
.venv\Scripts\activate
python app.py
```

### Terminal 2: Start the Streamlit UI

```powershell
cd D:\smartbank
.venv\Scripts\activate
python -m streamlit run dashboard.py
```

Open the Streamlit URL shown in the terminal (usually `http://localhost:8501`).

## Notes

- The Streamlit UI calls the API at `http://127.0.0.1:5000` by default.
- If you run the API on a different host/port, set this before starting Streamlit:

```powershell
$env:API_BASE_URL="http://127.0.0.1:5000"
```