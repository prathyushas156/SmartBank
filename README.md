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
- `dashboard.py` - Streamlit dashboard
- `db_config.py` - Database connection helper
- `routes/` - API routes
- `services/` - Business logic
- `models/` - Database operations
- `analytics/` - Dashboard/analytics support

## Prerequisites

- Python 3.10+
- MySQL running locally
- A MySQL database named `smartbank`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/prathyushas156/SmartBank.git
   cd SmartBank