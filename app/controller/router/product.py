from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection.postgresql import get_db
from service.product_service import infProduct_service
from dto.errors import BusinessException

router = APIRouter(prefix="/product", tags=["Products"])

@router.get("/")
def get_products(db: Session = Depends(get_db), query: str = None):
    try: 
        result = infProduct_service(db, query)
        return {"success": True, "data": result}
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=str(e)) 
    except Exception as e:          
        raise HTTPException(status_code=500, detail=str(e))