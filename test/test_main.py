import psycopg2
import pytest
import httpx
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from db import get_db_connection

# Mock get_db_connection to prevent real DB connections during tests
@pytest.fixture
def mock_db_conn():
    with patch("main.get_db_connection") as mock_get_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_db.return_value = mock_conn
        yield mock_cursor

# Client for testing
client = TestClient(app)

# ====================
# Authentication Tests
# ====================

@pytest.mark.asyncio
async def test_get_auth_config():
    response = await client.get("/auth-config/")
    assert response.status_code == 200
    data = response.json()
    assert "AUTH0_DOMAIN" in data
    assert "AUTH0_CLIENT_ID" in data
    assert "AUTH0_API_AUDIENCE" in data

# ====================
# Customer Tests
# ====================

def test_create_customer(mock_db_conn):
    # Mocking the fetchone result
    mock_db_conn.fetchone.return_value = {"customer_id": 1}

    # Input data
    customer_data = {
        "customer_code": "CUST001",
        "name": "John Doe",
        "telephone": "+254701234567",
        "location": "Nairobi"
    }

    # API request
    response = client.post("/customers/", json=customer_data)
    assert response.status_code == 201
    assert response.json()["message"] == "Customer created successfully"

def test_create_customer_conflict(mock_db_conn):
    # Simulate duplicate entry
    mock_db_conn.fetchone.return_value = None

    customer_data = {
        "customer_code": "CUST001",
        "name": "John Doe",
        "telephone": "+254701234567",
        "location": "Nairobi"
    }

    response = client.post("/customers/", json=customer_data)
    assert response.status_code == 409
    assert response.json()["detail"] == "Customer code already exists."

def test_list_customers(mock_db_conn):
    # Simulating database return value
    mock_db_conn.fetchall.return_value = [
        {"customer_id": 1, "customer_code": "CUST001", "name": "John Doe", "telephone": "+254701234567", "location": "Nairobi"}
    ]

    response = client.get("/customers/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["customer_code"] == "CUST001"

# ====================
# Order Tests
# ====================

def test_create_order(mock_db_conn):
    mock_db_conn.fetchone.return_value = {"order_id": 1}

    order_data = {
        "telephone": "+254701234567",
        "item": "Pizza",
        "amount": 1200,
        "order_time": "2024-11-10T14:20:00"
    }

    response = client.post("/orders/", json=order_data)
    assert response.status_code == 201
    assert response.json()["message"] == "Order created successfully and message sent successfully"

def test_create_order_fk_violation(mock_db_conn):
    # Simulate Foreign Key Violation
    mock_db_conn.execute.side_effect = psycopg2.errors.ForeignKeyViolation

    order_data = {
        "telephone": "+254700000000",
        "item": "Burger",
        "amount": 500
    }

    response = client.post("/orders/", json=order_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "The customer Telephone does not exist. Please provide a valid customer Telephone."

def test_list_orders(mock_db_conn):
    # Mock database fetchall return value
    mock_db_conn.fetchall.return_value = [
        {"order_id": 1, "telephone": "+254701234567", "item": "Pizza", "amount": 1200, "order_time": "2024-11-10T14:20:00"}
    ]

    response = client.get("/orders/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["item"] == "Pizza"
