import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection parameters
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


# Function to connect to the PostgreSQL server
def connect_to_server():
    try:
        with psycopg2.connect(
            dbname="postgres", user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        ) as conn:
            conn.autocommit = True
            return conn
    except Exception as e:
        print("Error connecting to PostgreSQL server:", e)
        return None


# Function to create the database if it does not exist
def create_database():
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
    try:
        with psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        ) as conn:
            with conn.cursor() as cur:

                # SQL Command to create customers table
                create_customers_table = """
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id SERIAL PRIMARY KEY,
                    customer_code VARCHAR(50) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    location VARCHAR(100)
                );
                """

                # SQL Command to create orders table
                create_orders_table = """
                CREATE TABLE IF NOT EXISTS orders (
                    order_id SERIAL PRIMARY KEY,
                    customer_id INTEGER REFERENCES customers(customer_id) ON DELETE CASCADE,
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
    try:
        with psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        ) as conn:
            with conn.cursor() as cur:

                # Insert sample customers
                customers_data = [
                    ("CUST001", "John Doe", "New York"),
                    ("CUST002", "Jane Smith", "Los Angeles"),
                    ("CUST003", "Alice Johnson", "Chicago"),
                    ("CUST004", "Bob Brown", "San Francisco"),
                ]
                cur.executemany(
                    """
                    INSERT INTO customers (customer_code, name, location)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (customer_code) DO NOTHING;
                    """,
                    customers_data,
                )

                # Insert sample orders
                orders_data = [
                    (1, "Laptop", 1200.00),
                    (2, "Smartphone", 800.00),
                    (1, "Headphones", 150.00),
                    (3, "Keyboard", 100.00),
                    (4, "Monitor", 300.00),
                ]
                cur.executemany(
                    """
                    INSERT INTO orders (customer_id, item, amount)
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
