from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection.postgresql import get_db
from service.shop_service import infShop_service
from dto.errors import BusinessException

router = APIRouter(prefix="/shop", tags=["Shops"])

@router.get("/inf")
def get_infShop(db: Session = Depends(get_db)):
    try: 
        result = infShop_service(db)
        return {"success": True, "data": result}
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=str(e)) 
    except Exception as e:          
        raise HTTPException(status_code=500, detail=str(e))
        
