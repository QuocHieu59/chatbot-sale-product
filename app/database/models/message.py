from sqlalchemy import Column, Text, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from database.connection.postgresql import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"
 
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("Message", back_populates="chat_session")
    ai_messages = relationship("AIMessage", back_populates="chat_session")

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    chat_session_id = Column(UUID, ForeignKey("chat_sessions.id"), nullable=False)
    sender_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    chat_session = relationship("ChatSession", back_populates="messages")
    sender = relationship("User")

class AIMessage(Base):
    __tablename__ = "ai_messages"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    chat_session_id = Column(UUID, ForeignKey("chat_sessions.id"), nullable=False)
    content = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    chat_session = relationship("ChatSession", back_populates="ai_messages") 