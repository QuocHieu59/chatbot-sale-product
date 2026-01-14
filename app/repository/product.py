from sqlalchemy.orm import Session
import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import uuid
import ast
import json

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
        
def color_product(product_id: str, selected_color: str, db: Session):
    # 1. Lấy product theo id
    product = db.query(Product).filter(Product.id == uuid.UUID(product_id)).first()
    print("product là:", product)
    if not product:
        return {"status": "error", "message": "Product not found"}

    # 2. Parse JSON string -> list dict
    try:
        raw = product.color_options
        parsed = ast.literal_eval(raw)
        fixed_json = json.dumps(parsed, ensure_ascii=False)
        print("raw color_options:", fixed_json)
        color_list = json.loads(fixed_json)   # [{'bạc': 2}, {'đen': 2}]
        print("color_list:", color_list)
    except Exception:
        return {"status": "error", "message": "Invalid color_options format"}

    # 3. Tìm color trong list
    found = False
    for color_obj in color_list:
        if selected_color in color_obj:
            if color_obj[selected_color] > 0:
                color_obj[selected_color] -= 1   # trừ đi 1
                found = True
            else:
                return {"status": "error", "message": f"Color '{selected_color}' is out of stock"}
    
    if not found:
        return {"status": "error", "message": f"Color '{selected_color}' not found in product"}

    # 4. Kiểm tra tổng tất cả số lượng
    total_quantity = sum(list(item.values())[0] for item in color_list)

    # Nếu tổng == 0 → stock = False
    if total_quantity == 0:
        product.status = False

    # 5. Lưu lại color_options (convert lại thành JSON)
    product.color_options = json.dumps(color_list, ensure_ascii=False)

    db.commit()
    db.refresh(product)

    return {
        "status": "success",
        "message": "Color updated",
        "remaining_colors": color_list,
        "stock": product.status
    }
