from typing import Optional
from pydantic import BaseModel
from contextvars import ContextVar
from uuid import UUID
from datetime import datetime

# Lưu user_id cho từng request (an toàn trong async)
current_user_id: ContextVar[str | None] = ContextVar("current_user_id", default=None)

# Nếu bạn muốn lưu thêm các biến khác, ví dụ thread_id
current_thread_id: ContextVar[str | None] = ContextVar("current_thread_id", default=None)
class OrderRequest(BaseModel):
    id_phone: str
    id_user: str
    customer_phone: str
    customer_address: str
    color: str
    info: str

class OrderUpdateRequest(BaseModel):
    order_id: str
    username: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    info: str
class OrderListRequest(BaseModel):
    id_user: str

class OrderDeleteRequest(BaseModel):
    order_id: str

class OrderResponse(BaseModel):
    id: UUID
    user_id: UUID
    total_amount: int
    status: str
    created_at: datetime    
    class Config:
        from_attributes = True