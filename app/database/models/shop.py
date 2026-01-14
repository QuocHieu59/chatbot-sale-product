from sqlalchemy import Column, String, DateTime, UUID
from datetime import datetime
import uuid

from database.connection.postgresql import Base

class Shop(Base):
    __tablename__ = "Infshops"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name_shop = Column(String, nullable=False)
    adress = Column(String, nullable=False)
    wrk_hrs = Column(String, nullable=False)
    link = Column(String, nullable=False)
    inf_staff = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    def __str__(self):
        return f"Tên shop: {self.name_shop} | Địa chỉ: {self.adress} | Giờ làm việc: {self.wrk_hrs} | Nhân viên tư vấn: {self.inf_staff} | google map: {self.link} "