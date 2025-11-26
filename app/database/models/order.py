from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, UUID
from datetime import datetime
import uuid
from database.connection.postgresql import Base
import uuid

class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    id_phone = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    id_user = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    username = Column(String, nullable=True)
    customer_phone = Column(String, nullable=False)
    customer_address = Column(String, nullable=False)
    info = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
