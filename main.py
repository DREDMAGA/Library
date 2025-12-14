import os
import pyodbc
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database credentials from environment variables
db_driver = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
db_server = os.getenv("DB_SERVER", "localhost,1433")
db_name = os.getenv("DB_NAME", "master")
db_user = os.getenv("DB_USER", "sa")
db_password = os.getenv("DB_PASSWORD")

if not db_password:
    raise ValueError(
        "DB_PASSWORD environment variable is required. Please create a .env file based on .env.example"
    )

conn = pyodbc.connect(
    f"Driver={{{db_driver}}};"
    f"Server={db_server};"
    f"Database={db_name};"
    f"UID={db_user};"
    f"PWD={db_password};"
    "TrustServerCertificate=yes;"
)
cursor = conn.cursor()

# Пример вызова процедуры select_pr
book_id = 1
cursor.execute("EXEC select_pr @book_id = ?", book_id)
row = cursor.fetchone()
print(row)
