# config_template.py
import os
from sqlalchemy import create_engine

# ===========================
# Database Configuration (Template)
# ===========================
DB_CONFIG = {
    "dialect": "postgresql",
    "username": "your_username_here",
    "password": "your_password_here",
    "host": "your_host_here",
    "port": "5432",
    "database": "your_database_here"
}

# Construct the connection string
DATABASE_URL = (
    f"{DB_CONFIG['dialect']}://{DB_CONFIG['username']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

# Create database engine
engine = create_engine(DATABASE_URL)
