# Library Database Project

Python application for interacting with SQL Server database.

## Prerequisites

- Python 3.x
- SQL Server (local or remote)
- ODBC Driver 18 for SQL Server

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   ```

3. Install dependencies:
   ```bash
   pip install pyodbc python-dotenv
   ```

4. Configure database connection:
   - Copy `.env.example` to `.env`
   - Update the database credentials in `.env` with your actual SQL Server password

   ```bash
   cp .env.example .env
   # Edit .env and set your DB_PASSWORD
   ```

5. Run the application:
   ```bash
   python main.py
   ```

## Configuration

The application uses environment variables for database configuration:

- `DB_DRIVER`: ODBC driver name (default: "ODBC Driver 18 for SQL Server")
- `DB_SERVER`: Server address and port (default: "localhost,1433")
- `DB_NAME`: Database name (default: "master")
- `DB_USER`: Database username (default: "sa")
- `DB_PASSWORD`: Database password (required)

## Troubleshooting

If you get a login error, make sure:
1. SQL Server is running
2. The password in `.env` matches your SQL Server SA password
3. SQL Server is configured to allow SQL authentication
4. The firewall allows connections on port 1433
