from sqlalchemy.orm import Session
from repository.shop import get_all_shop
from dto.errors import BusinessException


def infShop_service(db: Session):
    """Business logic for user login."""

    Shops = get_all_shop(db)
    
    if not Shops:
        raise BusinessException("Can't found any shop")
    return Shops
      