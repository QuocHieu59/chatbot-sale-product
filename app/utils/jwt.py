import os
from jose import jwt
import logging
from jose.exceptions import JWTError, ExpiredSignatureError
from datetime import datetime, timedelta
from dotenv import load_dotenv

from constants.const import SECRET_KEY, PUBLIC_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

logger = logging.getLogger(__name__)

load_dotenv()

def create_access_token(data: dict, expires_delta: timedelta = None):
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except JWTError as e:
        logger.error(f"JWT encode error: {e}")
        raise Exception("Không thể tạo access token")
    except Exception as e:
        logger.error(f"Unexpected error while creating token: {e}")
        raise

def create_refresh_token(data: dict):
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    except JWTError as e:
        logger.error(f"JWT encode error: {e}")
        raise Exception("Không thể tạo refresh token")
    except Exception as e:
        logger.error(f"Unexpected error while creating refresh token: {e}")
        raise

def decode_access_token(token: str):
    return jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM])
