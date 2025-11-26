from pydantic import BaseModel
from contextvars import ContextVar

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

