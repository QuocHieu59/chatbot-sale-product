from sqlalchemy.orm import Session
import logging
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from dto.errors import DatabaseError
from database.models.user import User

logger = logging.getLogger(__name__)

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Lấy user theo email."""
    try:
        return db.query(User).filter(User.email == email).first()
    except SQLAlchemyError as e:
        # rollback để tránh giữ trạng thái lỗi trong session
        db.rollback()
        # có thể log lỗi ở đây (tùy bạn setup logging)
        print(f"[DB ERROR] get_user_by_email: {e}")
        raise DatabaseError(f"Database error in get user by email: {e}")
    
def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
    """Lấy user theo ID."""
    try:
        return db.query(User).filter(User.id == str(user_id)).first()
    except SQLAlchemyError as e:
        db.rollback()
        print(f"[DB ERROR] get_user_by_id: {e}")
        raise DatabaseError(f"Database error in get user by id: {e}")


def create_user(db: Session, user: User) -> Optional[User]:
    """Tạo mới user trong DB."""
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError as e:
        db.rollback()
        print(f"[DB ERROR] create_user: {e}")
        raise DatabaseError(f"Database error in create user: {e}")