# insert_user.py
from database.connection.postgresql import SessionLocal
from database.models.user import User
from utils.hash import get_password_hash
import bcrypt

# Mở session
db = SessionLocal()

# Hash mật khẩu
password = "123456"


# Tạo user mới
new_user = User(
    name="Ngô Hiếu",
    email="ngohieu@example.com",
    password=get_password_hash(password),
)

# Lưu vào DB
db.add(new_user)
db.commit()
db.refresh(new_user)

print("✅ User created:", new_user.id, new_user.email)

db.close()
