from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from uuid import UUID

from database.connection.postgresql import get_db
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


def admin_required(userid = Depends(get_current_user), db: Session = Depends(get_db)):
    from database.models.user import User  # Import ở đây để tránh vòng lặp
    try:
        user = db.query(User).filter(User.id == userid).first()
        if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
        if user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin privileges required")
        return True
    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error"
        )
    