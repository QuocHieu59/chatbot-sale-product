from passlib.context import CryptContext
import hashlib

# Khởi tạo context dùng bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_text_hash(text: str) -> str:
    """Tạo mã hash (md5) để xác định dữ liệu đã thay đổi chưa."""
    return hashlib.md5((text or "").encode("utf-8")).hexdigest()