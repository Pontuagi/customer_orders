from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Pydantic models for customer input
class CustomerCreate(BaseModel):
    customer_code: str
    name: str
    telephone: str = Field(..., pattern=r"^\+?\d{10,15}$", description="Customer telephone number with optional country code")
    location: Optional[str] = None

# Pydantic model for order input
class OrderCreate(BaseModel):
    telephone: str = Field(..., pattern=r"^\+?\d{10,15}$", description="Customer telephone number with optional country code")
    item: str
    amount: float
    order_time: Optional[datetime] = None
