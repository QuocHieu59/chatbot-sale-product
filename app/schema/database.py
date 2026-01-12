from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

# Chat Session schemas
class ChatSessionBase(BaseModel):
    user_id: UUID

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSession(ChatSessionBase):
    id: UUID
    started_at: datetime
    ended_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Message schemas
class MessageBase(BaseModel):
    chat_session_id: UUID
    sender_id: UUID
    content: str

class MessageCreate(BaseModel):
    chat_session_id: UUID
    sender_id: UUID
    content: str

class Message(MessageCreate):
    id: UUID
    sent_at: datetime

    class Config:
        from_attributes = True

# AI Message schemas
class AIMessageBase(BaseModel):
    chat_session_id: UUID
    content: str

class AIMessageCreate(AIMessageBase):
    pass

class AIMessage(AIMessageBase):
    id: UUID
    sent_at: datetime

    class Config:
        from_attributes = True

class AIMessageList(BaseModel):
    messages: List[AIMessage]

# Combined Message schemas
class CombinedMessage(BaseModel):
    content: str
    type: str  # "ai" or "human"
    sent_at: datetime

    class Config:
        from_attributes = True

class CombinedMessageList(BaseModel):
    messages: List[CombinedMessage]

# Response schemas

class ChatSessionList(BaseModel):
    sessions: List[ChatSession]

class MessageList(BaseModel):
    messages: List[Message]

