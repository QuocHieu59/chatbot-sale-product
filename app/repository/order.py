from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from dto.errors import DatabaseError

from database.models.order import Order


def create_order(db: Session, order: Order) -> Optional[Order]:
    """Tạo mới order trong DB."""
    try:
        db.add(order)
        db.commit()
        db.refresh(order)
        return order
    except SQLAlchemyError as e:
        db.rollback()
        print(f"[DB ERROR] create_order: {e}")
        raise DatabaseError(f"Database error in create user: {e}")