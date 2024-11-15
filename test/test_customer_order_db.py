import unittest
from unittest.mock import patch, MagicMock
import psycopg2
from customer_order_db import connect_to_server, create_database, create_tables, insert_sample_data
import os


class TestCustomerOrderDB(unittest.TestCase):

    @patch("customer_order_db.psycopg2.connect")
    def test_connect_to_server_success(self, mock_connect):
        # Mock the connection object
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        # Test the connect_to_server function
        conn = connect_to_server()
        self.assertIsNotNone(conn)
        mock_connect.assert_called_once_with(
            dbname="postgres",
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )

    @patch("customer_order_db.psycopg2.connect")
    def test_connect_to_server_failure(self, mock_connect):
        # Simulate connection failure
        mock_connect.side_effect = Exception("Connection failed")

        # Test the connect_to_server function
        conn = connect_to_server()
        self.assertIsNone(conn)

    @patch("customer_order_db.connect_to_server")
    @patch("customer_order_db.psycopg2.connect")
    def test_create_database(self, mock_connect, mock_connect_to_server):
        mock_server_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_server_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect_to_server.return_value = mock_server_conn

        mock_cursor.fetchone.return_value = None
        create_database()

        mock_cursor.execute.assert_any_call("SELECT 1 FROM pg_database WHERE datname = %s", (os.getenv("DB_NAME"),))
        mock_cursor.execute.assert_any_call(unittest.mock.ANY)

    @patch("customer_order_db.psycopg2.connect")
    def test_create_tables(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        create_tables()

        mock_cursor.execute.assert_any_call(unittest.mock.ANY)
        mock_cursor.execute.assert_any_call(unittest.mock.ANY)

    @patch("customer_order_db.psycopg2.connect")
    def test_insert_sample_data(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        insert_sample_data()

        insert_customer_query = """
        INSERT INTO customers (customer_code, name, telephone, location)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (customer_code) DO NOTHING;
        """.strip()

        mock_cursor.executemany.assert_any_call(
            insert_customer_query,
            [
                ("CUST001", "John Doe", "+254701234567", "Nairobi"),
                ("CUST002", "Jane Smith", "+254712345678", "Mombasa"),
                ("CUST003", "Alice Johnson", "+254723456789", "Kisumu"),
                ("CUST004", "Bob Brown", "+254734567890", "Eldoret"),
            ]
        )




if __name__ == "__main__":
    unittest.main()
