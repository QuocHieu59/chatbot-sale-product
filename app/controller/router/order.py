import uuid
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from database.connection.postgresql import get_db
from service.order_service import order_service
from dto.order import OrderDeleteRequest, OrderListRequest, OrderRequest, OrderResponse, OrderUpdateRequest
from database.models.order import Order
from dto.errors import BusinessException, DatabaseError

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/")
def CreateOrder(request: OrderRequest, db: Session = Depends(get_db)):
    try: 
        result = order_service(db=db, id_phone=request.id_phone, id_user=request.id_user, customer_phone=request.customer_phone, customer_address=request.customer_address, info=request.info, color=request.color)
        return {"success": True, "data": result}
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=str(e)) 
    except Exception as e:          
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
def get_orders(request: OrderListRequest, db: Session = Depends(get_db)):
    try: 
        query = db.query(Order)
        query = query.filter(Order.id_user == uuid.UUID(request.id_user))
        orders = query.order_by(Order.created_at.desc()).all()
        return {"success": True, "data": orders}
    except Exception as e:          
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all")
def get_orders(db: Session = Depends(get_db)):
    try: 
        query = db.query(Order)
        orders = query.order_by(Order.created_at.desc()).all()
        return {"success": True, "data": orders}
    except Exception as e:          
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete")
def delete_order(request: OrderDeleteRequest,db: Session = Depends(get_db)):
    try:
        order_id = uuid.UUID(request.order_id)
        order = (
            db.query(Order)
            .filter(Order.id == order_id)
            .first()
        )
        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order không tồn tại"
            )
        db.delete(order)
        db.commit()
        return {
            "success": True,
            "order_id": str(order_id)
        }
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="order_id không đúng định dạng UUID"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@router.put("/update")
def update_order(
    request: OrderUpdateRequest,
    db: Session = Depends(get_db)
):
    try:
        order = (
            db.query(Order)
            .filter(Order.id == uuid.UUID(request.order_id))
            .first()
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order không tồn tại"
            )

        # chỉ cho cập nhật 2 field này
        if request.username is not None:
            order.username = request.username
        
        if request.info is not None:
            order.info =  request.info

        if request.customer_phone is not None:
            order.customer_phone = request.customer_phone

        if request.customer_address is not None:
            order.customer_address = request.customer_address

        db.commit()
        db.refresh(order)

        return {
            "success": True,
            "data": order
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
