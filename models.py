"""
Module to define Pydantic models for customer and order input.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class CustomerCreate(BaseModel):
    """
    Customer creation input model.
    """
    customer_code: str
    name: str
    telephone: str = Field(
        ...,
        pattern=r"^\+?\d{10,15}$",
        description="Customer telephone number with optional country code"
    )
    location: Optional[str] = None

class OrderCreate(BaseModel):
    """
    Order creation input model.
    """
    telephone: str = Field(
        ...,
        pattern=r"^\+?\d{10,15}$",
        description="Customer telephone number with optional country code"
    )
    item: str
    amount: float
    order_time: Optional[datetime] = None
