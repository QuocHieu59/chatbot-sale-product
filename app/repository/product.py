from sqlalchemy.orm import Session
import logging
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Any
from sqlalchemy import text
from dto.errors import DatabaseError
from database.models.product import Product

logger = logging.getLogger(__name__)

def filter_products(db: Session, query: str):
    """
    Thực thi truy vấn SQL trong PostgreSQL.
    
    Args:
        db (Session): phiên làm việc SQLAlchemy.
        query (str): câu lệnh SQL sinh ra.
    
    Returns:
        List[Any]: danh sách kết quả truy vấn.
    """
    try:
        result = db.execute(text(query))
        rows = result.mappings().all()
        return rows
    except SQLAlchemyError as e:
        db.rollback()
        print(f"[DB ERROR] execute_sql: {e}")
        raise DatabaseError(f"Database error while executing query: {e}")
        
