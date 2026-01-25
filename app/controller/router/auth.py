from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Header
from sqlalchemy.orm import Session

from database.connection.postgresql import get_db
from service.auth_service import login_service, register_service, get_me_service
from utils.jwt import decode_access_token, create_access_token
from dto.auth import LoginRequest, RegisterRequest
from dto.errors import BusinessException, DatabaseError

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
def login(request: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """Login user with email and password."""
    try: 
        result = login_service(db=db, email=request.email, password=request.password, response=response)
        return {"success": True, "data": result}
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=str(e)) 
    except Exception as e:          
        raise HTTPException(status_code=500, detail=str(e))
        
        

@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    try:
        result = register_service(db=db, email=request.email, password=request.password, name=request.name, age=request.age, repeat_password = request.repeat_password)
        return {"success": True, "data": result}
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/refresh") 
async def refresh_token(payload: dict):
    refresh_token = payload.get("refresh_token")
    data = decode_access_token(refresh_token)
    if not data or data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    access_token = create_access_token({"sub": data["sub"]})
    return {"access_token": access_token}

@router.get("/me")
def get_me(authorization: str = Header(None), db: Session = Depends(get_db)):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Unauthorized")
        token = authorization.split(" ")[1]
        print(token)
        if not token:
            return {"logged_in": False}
        result = get_me_service(db, token)
        return {"logged_in": True, "data": result}
    except:
        return {"logged_in": False}
        

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="access_token_user",
        path="/"
    )
    response.delete_cookie(
        key="refresh_token_user",
        path="/"
    )
    return {"message": "Logged out"}