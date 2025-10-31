from sqlalchemy.orm import Session
import logging
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from dto.errors import DatabaseError
from database.models.shop import Shop

logger = logging.getLogger(__name__)

def get_all_shop(db: Session) -> Optional[Shop]:
    try:
        return db.query(Shop).all()
    except SQLAlchemyError as e:
        # rollback để tránh giữ trạng thái lỗi trong session
        db.rollback()
        print(f"[DB ERROR] get_all_shop: {e}")
        raise DatabaseError(f"Database error in get all inf shop: {e}")