from sqlalchemy.orm import Session
from fastapi import Response

from database.models.user import User
from repository.user import get_user_by_email, create_user, get_user_by_id
from utils.hash import verify_password, get_password_hash
from utils.jwt import create_access_token, create_refresh_token, decode_access_token
from dto.errors import DatabaseError, BusinessException, SystemException



def login_service(db: Session, email: str, password: str, response: Response = None):
    """Business logic for user login."""

    user = get_user_by_email(db, email)
    
    if not user:
        raise BusinessException("User not found")
    if not verify_password(password, user.password):
        raise BusinessException("Incorrect password") 
    token_data = {"sub": str(user.id)}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    return {"user": user, "access_token": access_token, "refresh_token": refresh_token}
      

def register_service(db: Session, email: str, password: str, repeat_password: str, name: str, age: int):
    """Business logic for user registration."""
    
    if email == "" or password == "" or name == "" or age is None:
        raise BusinessException("Missing required fields")
    existing_user = get_user_by_email(db, email)
    if existing_user:
        raise BusinessException("User already exists")
    if password != repeat_password:
        raise BusinessException("Passwords do not match")
    if age <= 1 or age > 120:
        raise BusinessException("Invalid age")
    new_user = User(email=email, password=get_password_hash(password), name=name, age=age)
    user_created = create_user(db, new_user)
    return {"user": user_created}
   
def get_me_service(db: Session, token: str):
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    existing_user = get_user_by_id(db, user_id)
    if not existing_user:
        raise BusinessException("User not found")
    return {"id": existing_user.id, "email": existing_user.email, "name": existing_user.name, "role": existing_user.role}