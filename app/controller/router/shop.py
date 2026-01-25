from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from database.connection.postgresql import get_db
from service.shop_service import infShop_service
from dto.errors import BusinessException
from database.models.shop import Shop
from dto.auth import ShopCreate, ShopUpdate, ShopId
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

@router.get("/admin/list")
def get_all_shops(db: Session = Depends(get_db)):
    try:
        shops = db.query(Shop).all()
        return {
            "status": "success",
            "data": shops
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@router.post("/admin/create")
def create_shop(request: ShopCreate, db: Session = Depends(get_db)):
    try:
        new_shop = Shop(
            name_shop=request.name_shop,
            adress=request.adress,
            wrk_hrs=request.wrk_hrs,
            link=request.link,
            inf_staff=request.inf_staff
        )

        db.add(new_shop)
        db.commit()
        db.refresh(new_shop)

        return {
            "status": "success",
            "data": new_shop
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create shop: {str(e)}"
        )
    
@router.put("/admin/update")
def update_shop(request: ShopUpdate, db: Session = Depends(get_db)):
    try:
        shop = db.query(Shop).filter(
            Shop.id == uuid.UUID(request.id)
        ).first()

        if not shop:
            raise HTTPException(
                status_code=404,
                detail="Shop not found"
            )

        if request.name_shop is not None:
            shop.name_shop = request.name_shop
        if request.adress is not None:
            shop.adress = request.adress
        if request.wrk_hrs is not None:
            shop.wrk_hrs = request.wrk_hrs
        if request.link is not None:
            shop.link = request.link
        if request.inf_staff is not None:
            shop.inf_staff = request.inf_staff

        db.commit()
        db.refresh(shop)

        return {
            "status": "success",
            "data": shop
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update shop: {str(e)}"
        )

@router.delete("/admin/delete")
def delete_shop(request: ShopId, db: Session = Depends(get_db)):
    try:
        shop = db.query(Shop).filter(
            Shop.id == uuid.UUID(request.shop_id)
        ).first()

        if not shop:
            raise HTTPException(
                status_code=404,
                detail="Shop not found"
            )

        db.delete(shop)
        db.commit()

        return {
            "status": "success",
            "shop_id": request.shop_id
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete shop: {str(e)}"
        )
