from sqlalchemy import Column, String, DateTime, UUID, Float, Integer, Boolean
from datetime import datetime
import uuid

from database.connection.postgresql import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    current_price = Column(Float, nullable=False)
    color_options = Column(String, nullable=False)
    network_sp = Column(Integer, nullable=False)
    charge_tech = Column(Integer, nullable=False)
    screen_size = Column(String, nullable=False)
    ram = Column(String, nullable=False)
    os = Column(String, nullable=False)
    chip = Column(String, nullable=False)
    memory = Column(String, nullable=False)
    pin = Column(Integer, nullable=False)
    sale = Column(Float, nullable=False, default=0.0)
    status = Column(Boolean, nullable=False, default=True)
    phone_company = Column(String, nullable=False)
    url = Column(String, nullable=False)
    product_specs = Column(String, nullable=False)
    product_promotion = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)