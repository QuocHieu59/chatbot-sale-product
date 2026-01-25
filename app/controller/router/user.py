import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.models.user import User
from utils.hash import get_password_hash
from dto.auth import UserId, UserUpdate, UserInformation
from database.connection.postgresql import get_db
from middlewares.auth import admin_required


router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
def get_users(db: Session = Depends(get_db)):
     return []

@router.get("/admin/list")
def get_all_users(db: Session = Depends(get_db)):
     try:
          users = db.query(User).all()
          return {
               "status": "success",
               "data": users
          }
     except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/admin/create")
def create_user(request: UserInformation, db: Session = Depends(get_db)):
     try:
        existing_user = db.query(User).filter((User.email == request.email)).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="User already exists"
            )

        new_user = User(
            name=request.name,
            email=request.email,
            age=request.age,
            password=get_password_hash(request.password),  # hash nếu cần
            role=request.role
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "status": "success",
            "message": "User created successfully",
            "data": new_user
        }

     except HTTPException:
        raise
     except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create user: {str(e)}"
        )
    

@router.put("/admin/update")
def update_user(request: UserUpdate, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == uuid.UUID(request.id)).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        existing_user = (
                    db.query(User)
                    .filter(
                         User.email == request.email,
                         User.id != user.id
                    )
                    .first()
                    )
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="email already exists"
            )

        if request.name is not None:
            user.name = request.name
        if request.email is not None:
            user.email = request.email
        if request.age is not None:
            user.age = request.age
        if request.password is not None:
            user.password = get_password_hash(request.password)
        if request.role is not None:
            user.role = request.role

        db.commit()
        db.refresh(user)

        return {
            "status": "success",
            "data": user
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update user: {str(e)}"
        )

    

@router.delete("/admin/delete")
def delete_user(request: UserId, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        db.delete(user)
        db.commit()

        return {
            "status": "success",
            "user_id": request.user_id
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete user: {str(e)}"
        )

     
    