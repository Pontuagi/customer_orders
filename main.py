from fastapi import FastAPI, HTTPException, Depends, Request
from urllib.parse import urlencode
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from typing import List
from db import get_db_connection
from models import CustomerCreate, OrderCreate
from fastapi_auth0 import Auth0
import os
from dotenv import load_dotenv
import httpx
import psycopg2
from send_sms import SendSMS

"""
Module to handle the FastAPI application.
It contains the FastAPI application instance, the Auth0 configuration, and the routes for the application.
The routes include the login, register, and logout routes,as well as the customers, and orders endpoints.
The module also calls the SendSMS class for sending SMS messages.
"""

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Auth0 Configuration
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_API_AUDIENCE = os.getenv("AUTH0_API_AUDIENCE")
AUTH0_CALLBACK_URL = "http://127.0.0.1:8000/callback"

auth0 = Auth0(domain=AUTH0_DOMAIN, api_audience=AUTH0_API_AUDIENCE)
    
# Auth0 Login Route
@app.get("/login")
async def login():
    params = {
        "client_id": AUTH0_CLIENT_ID,
        "response_type": "code",
        "scope": "openid profile email",
        "redirect_uri": AUTH0_CALLBACK_URL,
    }
    auth_url = f"https://{AUTH0_DOMAIN}/authorize?" + urlencode(params)
    return RedirectResponse(url=auth_url)

# Register Route
@app.get("/register")
async def register():
    params = {
        "client_id": AUTH0_CLIENT_ID,
        "response_type": "code",
        "scope": "openid profile email",
        "redirect_uri": AUTH0_CALLBACK_URL,
        "screen_hint": "signup"
    }
    register_url = f"https://{AUTH0_DOMAIN}/authorize?" + urlencode(params)
    return RedirectResponse(url=register_url)

# Logout Route
@app.get("/logout")
async def logout():
    logout_url = (
        f"https://{AUTH0_DOMAIN}/v2/logout?"
        + urlencode({
            "client_id": AUTH0_CLIENT_ID,
            "returnTo": "http://127.0.0.1:5500/static/login.html"
        })
    )
    return RedirectResponse(url=logout_url)

@app.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return JSONResponse(status_code=400, content={"message": "Authorization code missing."})

    # Exchange code for access token
    token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "authorization_code",
        "client_id": AUTH0_CLIENT_ID,
        "client_secret": AUTH0_CLIENT_SECRET,
        "code": code,
        "redirect_uri": AUTH0_CALLBACK_URL,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(token_url, headers=headers, data=data)
            response.raise_for_status()  # Raise an HTTPError if the status is 4xx or 5xx
            token_data = response.json()
        except httpx.HTTPStatusError as e:
            # Handle HTTP errors, e.g., if the status is 400 or 500
            return JSONResponse(
                status_code=e.response.status_code,
                content={"message": f"Token exchange failed: {e.response.text}"}
            )
        except Exception as e:
            # Handle any other exceptions
            return JSONResponse(
                status_code=500,
                content={"message": f"An unexpected error occurred: {str(e)}"}
            )

    # Check if access_token is in the response
    if "access_token" not in token_data:
        return JSONResponse(status_code=400, content={"message": "Token exchange failed. Access token not found."})

    # Redirect to frontend with the access token
    redirect_to = f"http://127.0.0.1:8000/static/customer_orders.html#access_token={token_data['access_token']}"
    return RedirectResponse(url=redirect_to)


# Endpoint to add a new customer
@app.post("/customers/", status_code=201)
def create_customer(customer: CustomerCreate):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO customers (customer_code, name, telephone, location)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (customer_code) DO NOTHING
            RETURNING customer_id;
            """,
            (customer.customer_code, customer.name, customer.telephone, customer.location),
        )
        result = cur.fetchone()
        if not result:
            raise HTTPException(status_code=409, detail="Customer code already exists.")
        conn.commit()
        return {"customer_id": result["customer_id"], "message": "Customer created successfully"}
    finally:
        cur.close()
        conn.close()

# Endpoint to add a new order
@app.post("/orders/", status_code=201)
def create_order(order: OrderCreate):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO orders (telephone, item, amount, order_time)
            VALUES (%s, %s, %s, COALESCE(%s, CURRENT_TIMESTAMP))
            RETURNING order_id;
            """,
            (order.telephone, order.item, order.amount, order.order_time),
        )
        result = cur.fetchone()
        conn.commit()
    
        # Send the SMS using SendSMS class
        sms_service = SendSMS()
        sms_service.sending_order(order.telephone, order.item, order.amount, order.order_time)
        
        return {"order_id": result["order_id"], "message": "Order created successfully and message sent successfully"}
    except psycopg2.errors.ForeignKeyViolation:
        raise HTTPException(
            status_code=400,
            detail="The customer Telephone does not exist. Please provide a valid customer Telephone."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    finally:
        cur.close()
        conn.close()

# Endpoint to list all customers
@app.get("/customers/", status_code=200)
def list_customers():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM customers;")
        customers = cur.fetchall()
        return customers
    finally:
        cur.close()
        conn.close()

# Endpoint to list all orders
@app.get("/orders/", status_code=200)
def list_orders():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM orders;")
        orders = cur.fetchall()
        return orders
    finally:
        cur.close()
        conn.close()
