from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Header
from sqlalchemy.orm import Session
from database.connection.postgresql import get_db
from service.order_service import order_service
from dto.order import OrderRequest
from dto.errors import BusinessException, DatabaseError

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/")
def Order(request: OrderRequest, db: Session = Depends(get_db)):
    """Login user with email and password."""
    try: 
        result = order_service(db=db, id_phone=request.id_phone, id_user=request.id_user, customer_phone=request.customer_phone, customer_address=request.customer_address, info=request.info, color=request.color)
        return {"success": True, "data": result}
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=str(e)) 
    except Exception as e:          
        raise HTTPException(status_code=500, detail=str(e))
