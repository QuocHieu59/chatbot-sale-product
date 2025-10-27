from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection.postgresql import get_db


router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
def get_users(db: Session = Depends(get_db)):
     return []

