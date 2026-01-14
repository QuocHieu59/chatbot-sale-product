# Chat Session CRUD operations
from datetime import datetime
import logging
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from database.models.message import ChatSession, Message, AIMessage

logger = logging.getLogger(__name__)

def create_chat_session(db: Session, user_id: UUID) -> ChatSession:
    db_chat_session = ChatSession(user_id=user_id)
    db.add(db_chat_session)
    db.commit()
    db.refresh(db_chat_session)
    return db_chat_session

def get_chat_session(db: Session, session_id: UUID) -> Optional[ChatSession]:
    return db.query(ChatSession).filter(ChatSession.id == session_id).first()

def get_user_chat_sessions(db: Session, user_id: UUID, skip: int = 0, limit: int = 100) -> List[ChatSession]:
    return db.query(ChatSession).filter(ChatSession.user_id == user_id).offset(skip).limit(limit).all()

def end_chat_session(db: Session, session_id: UUID) -> Optional[ChatSession]:
    chat_session = get_chat_session(db, session_id)
    if chat_session:
        chat_session.ended_at = datetime.utcnow()
        db.commit()
        db.refresh(chat_session)
    return chat_session

# Message CRUD operations
def create_message(
    db: Session,
    chat_session_id: UUID,
    sender_id: UUID,
    content: str
) -> Message:
    """Create a new message."""
    try:
        print("đến đây chưa 1")
        # Ensure UUIDs are properly converted
        if isinstance(chat_session_id, str):
            chat_session_id = UUID(chat_session_id)
        if isinstance(sender_id, str):
            sender_id = UUID(sender_id)
            
        db_message = Message(
            chat_session_id=chat_session_id,
            sender_id=sender_id,
            content=content
        )
        print("đến đây chưa")
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating message: {str(e)}")
        raise

def get_chat_messages(
    db: Session, chat_session_id: UUID, skip: int = 0, limit: int = 100
) -> List[Message]:
    """Get messages for a chat session."""
    return (
        db.query(Message)
        .filter(Message.chat_session_id == chat_session_id)
        .order_by(Message.sent_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

# AI Message CRUD operations
def create_ai_message(
    db: Session,
    chat_session_id: UUID,
    content: str
) -> AIMessage:
    """Create a new AI message."""
    try:
        # Ensure UUID is properly converted
        if isinstance(chat_session_id, str):
            chat_session_id = UUID(chat_session_id)
            
        db_message = AIMessage(
            chat_session_id=chat_session_id,
            content=content
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating AI message: {str(e)}")
        raise

def get_chat_ai_messages(
    db: Session, chat_session_id: UUID, skip: int = 0, limit: int = 100
) -> List[AIMessage]:
    """Get AI messages for a chat session."""
    return (
        db.query(AIMessage)
        .filter(AIMessage.chat_session_id == chat_session_id)
        .order_by(AIMessage.sent_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_combined_chat_messages(
    db: Session, chat_session_id: UUID, skip: int = 0, limit: int = 100
) -> List[dict]:
    """Get all messages (both user and AI) for a chat session."""
    try:
        # Get user messages
        user_messages = (
            db.query(Message)
            .filter(Message.chat_session_id == chat_session_id)
            .order_by(Message.sent_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        # Get AI messages
        ai_messages = (
            db.query(AIMessage)
            .filter(AIMessage.chat_session_id == chat_session_id)
            .order_by(AIMessage.sent_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        # Combine and format messages
        combined_messages = []
        
        # Add user messages
        for msg in user_messages:
            combined_messages.append({
                "content": msg.content,
                "type": "human",
                "sent_at": msg.sent_at
            })
            
        # Add AI messages
        for msg in ai_messages:
            combined_messages.append({
                "content": msg.content,
                "type": "ai",
                "sent_at": msg.sent_at
            })
            
        # Sort all messages by sent_at
        combined_messages.sort(key=lambda x: x["sent_at"])
        
        return combined_messages
    except Exception as e:
        logger.error(f"Error getting combined messages: {str(e)}")
        raise 