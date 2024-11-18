"""
Module to test the database connection module.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import psycopg2
from db import get_db_connection

class TestDatabaseConnection(unittest.TestCase):
    """
    Class containing test cases for the database connection module.
    """

    @patch('psycopg2.connect')
    def test_get_db_connection(self, mock_connect):
        """
        Function to test the get_db_connection function.
        """
        # Create a mock connection object
        mock_conn = MagicMock()

        # Set the return value of the mocked connect function
        mock_connect.return_value = mock_conn

        # Call the function to test
        connection = get_db_connection()

        # Check if psycopg2.connect was called with the correct arguments
        mock_connect.assert_called_once_with(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            cursor_factory=psycopg2.extras.RealDictCursor
        )

        # Assert that the function returns the mock connection object
        self.assertEqual(connection, mock_conn)

if __name__ == "__main__":
    unittest.main()
