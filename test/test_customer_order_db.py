"""
Module for testing the customer_order_db module.

Contains a class TestCustomerOrderDB that inherits from unittest.TestCase.
The class contains the following methods:
test_connect_to_server_success: Tests the connect_to_server function with a successful connection.
test_connect_to_server_failure: Tests the connect_to_server function with a failed connection.
test_create_database_success: Tests the create_database function with successful database creation.
"""

import os
import unittest
from unittest.mock import patch, MagicMock
# import psycopg2
from customer_order_db import connect_to_server, create_database, create_tables, insert_sample_data


class TestCustomerOrderDB(unittest.TestCase):
    """
    Class containing the test functions for the customer_order_db module.
    """
    @patch("customer_order_db.psycopg2.connect")
    def test_connect_to_server_success(self, mock_connect):
        """
        Function to test the connect_to_server function.
        """
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
        """
        Fuction to test the connect_to_server function with a failed connection.
        """
        # Simulate connection failure
        mock_connect.side_effect = Exception("Connection failed")

        # Test the connect_to_server function
        conn = connect_to_server()
        self.assertIsNone(conn)

    @patch("customer_order_db.connect_to_server")
    @patch("customer_order_db.psycopg2.connect")
    def test_create_database(self, mock_connect, mock_connect_to_server):
        """
        Test the create_database function.
        """
        mock_server_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_server_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect_to_server.return_value = mock_server_conn

        mock_cursor.fetchone.return_value = None
        create_database()

        mock_cursor.execute.assert_any_call("SELECT 1 FROM pg_database WHERE datname = %s", (os.getenv("DB_NAME"),))
        mock_cursor.execute.assert_any_call(unittest.mock.ANY)




if __name__ == "__main__":
    unittest.main()
