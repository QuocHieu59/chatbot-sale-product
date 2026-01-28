from math import ceil
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import uuid

from dto.product import ProductCreateRequest, ProductUpdateRequest
from dto.product import ProductDeleteRequest
from database.connection.postgresql import get_db
from database.models.product import Product
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

@router.get("/all")
def get_all_products(page: int = Query(0, ge=0), size: int = Query(20, ge=1, le=100),db: Session = Depends(get_db)):
    try:
        total = db.query(Product).count()

        products = (
            db.query(Product)
            .order_by(Product.created_at.desc())
            .offset(page * size)
            .limit(size)
            .all()
        )

        total_pages = ceil(total / size) if size else 0
        last = (page >= total_pages - 1)

        return {
            "success": True,
            "data": {
                "content": products,        # danh sách item
                "page": page,
                "size": size,
                "totalElements": total,
                "totalPages": total_pages,
                "last": last
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/create")
def create_product(
    request: ProductCreateRequest,
    db: Session = Depends(get_db)
):
    try:
        product = Product(
            name=request.name,
            current_price=request.current_price,
            color_options=request.color_options,
            network_sp=request.network_sp,
            charge_tech=request.charge_tech,
            screen_size=request.screen_size,
            ram=request.ram,
            os=request.os,
            chip=request.chip,
            memory=request.memory,
            pin=request.pin,
            sale=request.sale,
            status=request.status,
            phone_company=request.phone_company,
        )

        db.add(product)
        db.commit()
        db.refresh(product)

        return {"success": True, "data": product}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update")
def update_product(
    request: ProductUpdateRequest,
    db: Session = Depends(get_db)
):
    try:
        product_id = uuid.UUID(request.product_id)

        product = (
            db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product không tồn tại"
            )

        # cập nhật các field nếu có gửi lên
        if request.name is not None:
            product.name = request.name

        if request.current_price is not None:
            product.current_price = request.current_price

        if request.color_options is not None:
            product.color_options = request.color_options

        if request.network_sp is not None:
            product.network_sp = request.network_sp

        if request.charge_tech is not None:
            product.charge_tech = request.charge_tech

        if request.screen_size is not None:
            product.screen_size = request.screen_size

        if request.ram is not None:
            product.ram = request.ram

        if request.os is not None:
            product.os = request.os

        if request.chip is not None:
            product.chip = request.chip

        if request.memory is not None:
            product.memory = request.memory

        if request.pin is not None:
            product.pin = request.pin

        if request.sale is not None:
            product.sale = request.sale

        if request.status is not None:
            product.status = request.status

        if request.phone_company is not None:
            product.phone_company = request.phone_company

        if request.url is not None:
            product.url = request.url

        if request.product_specs is not None:
            product.product_specs = request.product_specs

        if request.product_promotion is not None:
            product.product_promotion = request.product_promotion

        db.commit()
        db.refresh(product)

        return {"success": True, "data": product}

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="product_id không đúng định dạng UUID"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete")
def delete_product(
    request: ProductDeleteRequest,
    db: Session = Depends(get_db)
):
    try:
        product_id = uuid.UUID(request.product_id)
        #print("Deleting product ID:", product_id)
        product = (
            db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product không tồn tại"
            )

        db.delete(product)
        db.commit()

        return {
            "success": True,
            "product_id": str(product_id)
        }

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="product_id không đúng định dạng UUID"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))