from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.crud.order import (
    get_order_by_id, get_order_by_order_id, get_orders, count_orders,
    create_order, update_order, delete_order
)
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse
from app.schemas.user import PaginatedResponse
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[OrderResponse])
async def get_orders_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get order list with optional filters"""
    total = count_orders(db, user_id=user_id, status=status)
    orders = get_orders(db, skip=skip, limit=limit, user_id=user_id, status=status)
    return PaginatedResponse(total=total, skip=skip, limit=limit, items=orders)


@router.get("/stats/overview")
async def get_orders_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get order statistics overview"""
    total_orders = count_orders(db)
    pending_orders = count_orders(db, status="pending")
    confirmed_orders = count_orders(db, status="confirmed")
    paid_orders = count_orders(db, status="paid")
    shipped_orders = count_orders(db, status="shipped")
    delivered_orders = count_orders(db, status="delivered")
    cancelled_orders = count_orders(db, status="cancelled")
    refunded_orders = count_orders(db, status="refunded")
    
    return {
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "confirmed_orders": confirmed_orders,
        "paid_orders": paid_orders,
        "shipped_orders": shipped_orders,
        "delivered_orders": delivered_orders,
        "cancelled_orders": cancelled_orders,
        "refunded_orders": refunded_orders
    }


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_details(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get order details by ID"""
    order = get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order


@router.get("/order-id/{order_id_str}", response_model=OrderResponse)
async def get_order_by_order_id_endpoint(
    order_id_str: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get order details by order_id string"""
    order = get_order_by_order_id(db, order_id_str)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_new_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new order"""
    if get_order_by_order_id(db, order.order_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order ID already exists"
        )
    
    try:
        return create_order(db, order)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{order_id}", response_model=OrderResponse)
async def update_existing_order(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update order"""
    order = get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    updated_order = update_order(db, order_id, order_update)
    return updated_order


@router.delete("/{order_id}")
async def delete_existing_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete order"""
    order = get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    delete_order(db, order_id)
    return {"message": "Order deleted successfully"}
