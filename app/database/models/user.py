from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, UUID
from datetime import datetime
from sqlalchemy.orm import relationship
import uuid

from database.connection.postgresql import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False)
    age = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    chat_sessions = relationship("ChatSession", back_populates="user")
    
