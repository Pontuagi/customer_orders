"""
db.py: Module for managing database operations.

This module provides functionality to connect to a PostgreSQL database,
create tables, and perform CRUD operations.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


def get_db_connection():
    """
    Connect to the PostgreSQL server.

    Returns:
        psycopg2.connection: Connection object to the PostgreSQL server.
    """
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        cursor_factory=RealDictCursor
    )
    return conn

# Function to connect to the PostgreSQL server
def connect_to_server():
    """
    Connect to the PostgreSQL server.

    Returns:
        psycopg2.connection: Connection object to the PostgreSQL server.
    """
    try:
        with psycopg2.connect(
            dbname="postgres", user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        ) as conn:
            conn.autocommit = True
            return conn
    except Exception as e:
        print("Error connecting to PostgreSQL server:", e)
        return None
