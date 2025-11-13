import os
import streamlit as st
from sqlalchemy import create_engine

# ===============================
# CLOUD DATABASE CONFIG (FROM SECRETS)
# ===============================

DB_CONFIG = {
    "dialect": st.secrets["DB_DIALECT"],  # ← FIX 1: use DBDIALECT from secrets.toml
    "username": st.secrets["DB_USER"],
    "password": st.secrets["DB_PASS"],
    "host": st.secrets["DB_HOST"],
    "port": st.secrets["DB_PORT"],
    "database": st.secrets["DB_NAME"],
}

DATABASE_URL = (
    f"{DB_CONFIG['dialect']}://{DB_CONFIG['username']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

engine = create_engine(DATABASE_URL)

# ===============================
# DIRECTORIES THAT EXIST IN STREAMLIT CLOUD
# ===============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RAW_DATA_PATH = os.path.join(BASE_DIR, "Data", "raw files")
PROCESSED_PATH = os.path.join(BASE_DIR, "Data", "Processed files")
LOG_DIR = os.path.join(BASE_DIR, "logs")
REPORT_PATH = os.path.join(BASE_DIR, "Reports")

SQL_QUERY_PATH1 = os.path.join(BASE_DIR, "Sqlqueries", "NodalOfficersqlQueries.sql")
SQL_QUERY_PATH2 = os.path.join(BASE_DIR, "Sqlqueries", "NodalAnalysisReport.sql")

FONT_PATH = os.path.join(BASE_DIR, "fonts", "Candara.ttf")

# Create folders if missing
for path in [RAW_DATA_PATH, PROCESSED_PATH, LOG_DIR, REPORT_PATH]:
    os.makedirs(path, exist_ok=True)
