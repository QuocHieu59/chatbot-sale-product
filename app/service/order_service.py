from sqlalchemy.orm import Session
import uuid

from database.models.order import Order
from database.models.user import User
from repository.order import create_order
from repository.product import color_product
from dto.errors import DatabaseError, BusinessException, SystemException

def order_service(db: Session, id_phone: str, id_user: str, customer_phone: str, customer_address: str, info: str, color: str):
    """Business logic for create order."""
    user = db.query(User).filter(User.id == uuid.UUID(id_user)).first()
    if not user:
        raise BusinessException("User does not exist")
    result = color_product(db=db, product_id=id_phone, selected_color=color)
    #print("result từ color_product:", result)
    if result['status'] == "error":
        raise BusinessException(str(result['message']))
    else:
        new_order = Order(id_phone=uuid.UUID(id_phone), id_user=uuid.UUID(id_user), username = user.name, customer_phone=customer_phone, customer_address=customer_address, info=info)
        order_created = create_order(db, new_order)
        return {
            "username": order_created.username,
            "customer_phone": order_created.customer_phone,
            "customer_address": order_created.customer_address,
            "info": order_created.info,
        }