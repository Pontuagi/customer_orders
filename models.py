from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Pydantic models for customer input
class CustomerCreate(BaseModel):
    customer_code: str
    name: str
    location: Optional[str] = None

# Pydantic model for order input
class OrderCreate(BaseModel):
    customer_id: int
    item: str
    amount: float
    order_time: Optional[datetime] = None
