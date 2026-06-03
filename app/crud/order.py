from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderUpdate


def get_order_by_id(db: Session, order_id: int) -> Optional[Order]:
    """Get order by ID"""
    return db.query(Order).filter(Order.id == order_id).first()


def get_order_by_order_id(db: Session, order_id: str) -> Optional[Order]:
    """Get order by order_id string"""
    return db.query(Order).filter(Order.order_id == order_id).first()


def get_orders_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
    """Get orders by user ID"""
    return db.query(Order).filter(Order.user_id == user_id).offset(skip).limit(limit).all()


def count_orders(db: Session, user_id: Optional[int] = None, status: Optional[str] = None) -> int:
    """Count orders with optional filters"""
    query = db.query(Order)
    if user_id is not None:
        query = query.filter(Order.user_id == user_id)
    if status is not None:
        query = query.filter(Order.status == status)
    return query.count()


def get_orders(db: Session, skip: int = 0, limit: int = 100, user_id: Optional[int] = None,
               status: Optional[str] = None) -> List[Order]:
    """Get order list with optional filters"""
    query = db.query(Order)
    if user_id is not None:
        query = query.filter(Order.user_id == user_id)
    if status is not None:
        query = query.filter(Order.status == status)
    return query.offset(skip).limit(limit).all()


def create_order(db: Session, order: OrderCreate) -> Order:
    """Create new order"""
    db_order = Order(
        order_id=order.order_id,
        user_id=order.user_id,
        total_amount=order.total_amount,
        status=order.status,
        remarks=order.remarks,
        payment_method=order.payment_method,
        invoice_info=order.invoice_info,
    )
    try:
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order
    except IntegrityError:
        db.rollback()
        raise ValueError("Order ID already exists")


def update_order(db: Session, order_id: int, order_update: OrderUpdate) -> Optional[Order]:
    """Update order"""
    db_order = get_order_by_id(db, order_id)
    if not db_order:
        return None

    update_data = order_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_order, field, value)

    db.commit()
    db.refresh(db_order)
    return db_order


def delete_order(db: Session, order_id: int) -> bool:
    """Delete order"""
    db_order = get_order_by_id(db, order_id)
    if not db_order:
        return False
    db.delete(db_order)
    db.commit()
    return True
