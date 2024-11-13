from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
from db import get_db_connection
from models import CustomerCreate, OrderCreate
from fastapi_auth0 import Auth0, Auth0User
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Auth0 Configuration
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_API_AUDIENCE = os.getenv("AUTH0_API_AUDIENCE")

auth0 = Auth0(domain=AUTH0_DOMAIN, api_audience=AUTH0_API_AUDIENCE)

# share the auth0 instance with frontend
@app.get("/auth-config/")
async def get_auth_config():
    return JSONResponse(content={
        "AUTH0_DOMAIN": AUTH0_DOMAIN,
        "AUTH0_CLIENT_ID": AUTH0_CLIENT_ID,
        "AUTH0_API_AUDIENCE": AUTH0_API_AUDIENCE,
    })

# Endpoint to add a new customer
@app.post("/customers/", status_code=201, dependencies=[Depends(auth0.get_user)])
def create_customer(customer: CustomerCreate):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO customers (customer_code, name, location)
            VALUES (%s, %s, %s)
            ON CONFLICT (customer_code) DO NOTHING
            RETURNING customer_id;
            """,
            (customer.customer_code, customer.name, customer.location),
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
@app.post("/orders/", status_code=201, dependencies=[Depends(auth0.get_user)])
def create_order(order: OrderCreate):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO orders (customer_id, item, amount, order_time)
            VALUES (%s, %s, %s, COALESCE(%s, CURRENT_TIMESTAMP))
            RETURNING order_id;
            """,
            (order.customer_id, order.item, order.amount, order.order_time),
        )
        result = cur.fetchone()
        conn.commit()
        return {"order_id": result["order_id"], "message": "Order created successfully"}
    finally:
        cur.close()
        conn.close()

# Endpoint to list all customers
@app.get("/customers/", status_code=200, dependencies=[Depends(auth0.get_user)])
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
@app.get("/orders/", status_code=200,  dependencies=[Depends(auth0.get_user)])
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
