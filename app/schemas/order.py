from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class OrderBase(BaseModel):
    user_id: int
    total_amount: float
    status: str = "pending"
    remarks: Optional[str] = None
    payment_method: Optional[str] = None
    invoice_info: Optional[str] = None


class OrderCreate(OrderBase):
    order_id: str


class OrderUpdate(BaseModel):
    total_amount: Optional[float] = None
    status: Optional[str] = None
    remarks: Optional[str] = None
    payment_method: Optional[str] = None
    invoice_info: Optional[str] = None


class OrderResponse(BaseModel):
    id: int
    order_id: str
    user_id: int
    total_amount: float
    status: str
    remarks: Optional[str] = None
    payment_method: Optional[str] = None
    invoice_info: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
