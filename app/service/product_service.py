from sqlalchemy.orm import Session

from repository.product import filter_products
from dto.errors import BusinessException

def infProduct_service(db: Session, query: str):
    """Business logic for product."""

    Products = filter_products(db, query)
    
    if not Products:
        raise BusinessException("Can't found any shop")
    return Products
      