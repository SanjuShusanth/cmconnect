import os
from sqlalchemy import create_engine

# ==============================
# Database Configuration
# ==============================
DB_CONFIG = {
    "dialect": "postgresql",
    "username": "avnadmin",
    "password": "AVNS_0RqM2QO8lu8nstmTVzW",
    "host": "cmconnect2025-26-sanjushusanth-a5cb.i.aivencloud.com",
    "port": "11350",
    "database": "defaultdb"
}

# Construct the connection string
DATABASE_URL = (
    f"{DB_CONFIG['dialect']}://{DB_CONFIG['username']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

# Create database engine
engine = create_engine(DATABASE_URL)

# ==============================
# Directory Paths
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data folders
RAW_DATA_PATH = os.path.join(BASE_DIR, "Data", "raw files")
PROCESSED_PATH = os.path.join(BASE_DIR, "Data", "Processed files")

# Log folder (folder only — we’ll specify filenames per script)
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Report output folder
REPORT_PATH = os.path.join(BASE_DIR, "Reports")

# SQL queries folder
SQL_QUERY_PATH1 = os.path.join(BASE_DIR, "Sqlqueries", "NodalOfficersqlQueries.sql")
SQL_QUERY_PATH2 = os.path.join(BASE_DIR, "Sqlqueries", "NodalAnalysisReport.sql")

# test report

output_file_path = os.path.join(BASE_DIR, "Data", "Output files")

# Font 

FONT_PATH = os.path.join(BASE_DIR, "fonts","Candara.ttf") 

# Templates (for Word, PDF, or PPT templates in future)
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates")

# ==============================
# Ensure folders exist
# ==============================
for path in [RAW_DATA_PATH, PROCESSED_PATH, LOG_DIR, REPORT_PATH]:
    os.makedirs(path, exist_ok=True)
