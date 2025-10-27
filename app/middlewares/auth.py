from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from uuid import UUID
from utils.jwt import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        user_id = UUID(user_id)  # chuyển lại dạng UUID nếu cần
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user_id
