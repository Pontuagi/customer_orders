"""
Test file to test the main FastAPI application with pytest.
"""

from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from main import app

# Create a test client
client = TestClient(app)

# Mock get_db_connection globally in this module
@pytest.fixture(scope="function")
def mock_db_connection():
    """
    Function to mock the get_db_connection function.
    """
    with patch('main.get_db_connection') as mock_conn:
        # Set up the mock connection and cursor
        mock_conn_instance = MagicMock()
        mock_cursor = MagicMock()
        mock_conn_instance.cursor.return_value = mock_cursor
        mock_conn.return_value = mock_conn_instance

        yield mock_cursor, mock_conn_instance

        # Ensure resources are closed
        mock_cursor.close.assert_called_once()
        mock_conn_instance.close.assert_called_once()

# Test customer creation endpoint
def test_create_customer(mock_db_connection):
    """
    Function to test the create customer endpoint.
    """
    mock_cursor, _ = mock_db_connection

    # Mock the cursor's fetchone method to simulate returning a customer ID
    mock_cursor.fetchone.return_value = {"customer_id": 1}

    # Define test input data
    test_data = {
        "customer_code": "CUST001",
        "name": "John Doe",
        "telephone": "1234567890",
        "location": "New York"
    }

    # Make a POST request to the create customer endpoint
    response = client.post("/customers/", json=test_data)

    # Check the response status and data
    assert response.status_code == 201
    assert response.json() == {"customer_id": 1, "message": "Customer created successfully"}

    # Verify the SQL query execution
    mock_cursor.execute.assert_called_once()
    assert "INSERT INTO customers" in mock_cursor.execute.call_args[0][0]

# Test order creation endpoint
@patch('main.SendSMS')
def test_create_order(mock_send_sms, mock_db_connection):
    """
    Function to test the create order endpoint.
    """
    mock_cursor, _ = mock_db_connection

    # Mock SMS service
    mock_sms_instance = mock_send_sms.return_value
    mock_sms_instance.sending_order.return_value = None

    # Mock the cursor's fetchone method to simulate returning an order ID
    mock_cursor.fetchone.return_value = {"order_id": 1}

    # Define test input data
    test_data = {
        "telephone": "1234567890",
        "item": "Pizza",
        "amount": 20.0,
        "order_time": None
    }

    # Make a POST request to the create order endpoint
    response = client.post("/orders/", json=test_data)

    # Check the response status and data
    assert response.status_code == 201
    assert response.json() == {"order_id": 1, "message": "Order created successfully and message sent successfully"}

    # Verify the SQL query execution
    mock_cursor.execute.assert_called_once()
    assert "INSERT INTO orders" in mock_cursor.execute.call_args[0][0]

    # Verify SMS was sent
    mock_sms_instance.sending_order.assert_called_once_with("1234567890", "Pizza", 20.0, None)

# Test customer listing endpoint
def test_list_customers(mock_db_connection):
    """
    Funnction to test the list customers endpoint.
    """
    mock_cursor, _ = mock_db_connection

    # Mock the cursor's fetchall method to simulate returning a list of customers
    mock_cursor.fetchall.return_value = [
        {"customer_id": 1, "name": "John Doe", "telephone": "1234567890", "location": "New York"}
    ]

    # Make a GET request to the list customers endpoint
    response = client.get("/customers/")

    # Check the response status and data
    assert response.status_code == 200
    assert response.json() == [
        {"customer_id": 1, "name": "John Doe", "telephone": "1234567890", "location": "New York"}
    ]

    # Verify the SQL query execution
    mock_cursor.execute.assert_called_once_with("SELECT * FROM customers;")

# Test order listing endpoint
def test_list_orders(mock_db_connection):
    """
    Function to test the list orders endpoint.
    """
    mock_cursor, _ = mock_db_connection

    # Mock the cursor's fetchall method to simulate returning a list of orders
    mock_cursor.fetchall.return_value = [
        {"order_id": 1, "telephone": "1234567890", "item": "Pizza", "amount": 20.0, "order_time": "2024-11-16T12:00:00"}
    ]

    # Make a GET request to the list orders endpoint
    response = client.get("/orders/")

    # Check the response status and data
    assert response.status_code == 200
    assert response.json() == [
        {"order_id": 1, "telephone": "1234567890", "item": "Pizza", "amount": 20.0, "order_time": "2024-11-16T12:00:00"}
    ]

    # Verify the SQL query execution
    mock_cursor.execute.assert_called_once_with("SELECT * FROM orders;")
