"""
Module to create and manage the customer_order_db database.
This module provides functions to create the database, create tables, insert sample data.
"""

from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql
from db import connect_to_server, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

load_dotenv()

# Function to create the database if it does not exist
def create_database():
    """
    Create the customer_order_db database if it does not exist.
    """
    conn = connect_to_server()
    if conn is None:
        return
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,)
            )
            if not cur.fetchone():
                cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
                print(f"Database '{DB_NAME}' created successfully.")
            else:
                print(f"Database '{DB_NAME}' already exists.")
    finally:
        conn.close()


# Function to create tables in the customer_order_db
def create_tables():
    """
    Create tables for customers and orders in the customer_order_db database.
    """
    try:
        with psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS orders CASCADE;")
                cur.execute("DROP TABLE IF EXISTS customers CASCADE;")

                # SQL Command to create customers table
                create_customers_table = """
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id SERIAL PRIMARY KEY,
                    customer_code VARCHAR(50) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    telephone VARCHAR(15) UNIQUE NOT NULL,
                    location VARCHAR(100)
                );
                """

                # SQL Command to create orders table
                create_orders_table = """
                CREATE TABLE IF NOT EXISTS orders (
                    order_id SERIAL PRIMARY KEY,
                    telephone VARCHAR(15) REFERENCES customers(telephone) ON DELETE CASCADE,
                    item VARCHAR(255) NOT NULL,
                    amount NUMERIC(10, 2) NOT NULL CHECK (amount >= 0),
                    order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """

                # Execute table creation
                cur.execute(create_customers_table)
                cur.execute(create_orders_table)

                print("Tables created successfully.")
    except Exception as e:
        print("Error creating tables:", e)


# Function to insert sample data
def insert_sample_data():
    """
    Insert sample data into the customers and orders tables.
    """
    try:
        with psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        ) as conn:
            with conn.cursor() as cur:

                # Insert sample customers with telephone numbers
                customers_data = [
                    ("CUST001", "John Doe", "+254701234567", "Nairobi"),
                    ("CUST002", "Jane Smith", "+254712345678", "Mombasa"),
                    ("CUST003", "Alice Johnson", "+254723456789", "Kisumu"),
                    ("CUST004", "Bob Brown", "+254734567890", "Eldoret"),
                ]
                cur.executemany(
                    """
                    INSERT INTO customers (customer_code, name, telephone, location)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (customer_code) DO NOTHING;
                    """,
                    customers_data,
                )

                # Insert sample orders using telephone numbers
                orders_data = [
                    ("+254701234567", "Laptop", 1200.00),
                    ("+254712345678", "Smartphone", 800.00),
                    ("+254701234567", "Headphones", 150.00),
                    ("+254723456789", "Keyboard", 100.00),
                    ("+254734567890", "Monitor", 300.00),
                ]
                cur.executemany(
                    """
                    INSERT INTO orders (telephone, item, amount)
                    VALUES (%s, %s, %s);
                    """,
                    orders_data,
                )

                print("Sample data inserted successfully.")
    except Exception as e:
        print("Error inserting sample data:", e)


if __name__ == "__main__":
    create_database()
    create_tables()
    insert_sample_data()
