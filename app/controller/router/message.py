from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from database.connection.postgresql import get_db
from database.models.message import Message
from repository.message import (
    create_chat_session,
    get_chat_session,
    get_user_chat_sessions,
    end_chat_session
)

from repository.user import get_user_by_id
from repository.message import (
    create_message,
    get_chat_messages,
    create_ai_message,
    get_chat_ai_messages,
    get_combined_chat_messages  
)
from schema.database import (
    ChatSession as ChatSessionSchema,
    ChatSessionCreate,
    ChatSessionList,
    Message as MessageSchema,
    MessageCreate,
    MessageList,
    AIMessage as AIMessageSchema,
    AIMessageCreate,
    AIMessageList,
    CombinedMessageList
)

router = APIRouter(prefix="/messages", tags=["Messages"])

# Chat Session endpoints
@router.post("/chat-sessions", response_model=ChatSessionSchema)
def create_new_chat_session(session: ChatSessionCreate, db: Session = Depends(get_db)):
    return create_chat_session(db=db, user_id=session.user_id)

@router.get("/chat-sessions/{session_id}", response_model=ChatSessionSchema)
def read_chat_session(session_id: UUID, db: Session = Depends(get_db)):
    db_session = get_chat_session(db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return db_session

@router.get("/users/{user_id}/chat-sessions", response_model=ChatSessionList)
def read_user_chat_sessions(user_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sessions = get_user_chat_sessions(db, user_id=user_id, skip=skip, limit=limit)
    return ChatSessionList(sessions=sessions)

@router.post("/chat-sessions/{session_id}/end", response_model=ChatSessionSchema)
def end_session(session_id: UUID, db: Session = Depends(get_db)):
    db_session = end_chat_session(db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return db_session

# Message endpoints
@router.post("/messages", response_model=MessageSchema)
def create_new_message(message: MessageCreate, db: Session = Depends(get_db)):
    """Create a new message."""
    try:
        
        # Verify chat session exists
        chat_session = get_chat_session(db, message.chat_session_id)
       
        if not chat_session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # Verify sender exists
        sender = get_user_by_id(db, message.sender_id)
        if not sender:
            raise HTTPException(status_code=404, detail="Sender not found")
        
        # Create message
        db_message = create_message(
            db=db,
            chat_session_id=message.chat_session_id,
            sender_id=message.sender_id,
            content=message.content
        )
        
        return db_message
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/messages/{message_id}", response_model=MessageSchema)
def read_message(message_id: UUID, db: Session = Depends(get_db)):
    """Get a specific message by ID."""
    try:
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        return message
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat-sessions/{session_id}/messages", response_model=MessageList)
def read_chat_messages(session_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all messages for a chat session."""
    try:
        messages = get_chat_messages(db, chat_session_id=session_id, skip=skip, limit=limit)
        return MessageList(messages=messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# AI Message endpoints
@router.post("/ai-messages", response_model=AIMessageSchema)
def create_new_ai_message(message: AIMessageCreate, db: Session = Depends(get_db)):
    """Create a new AI message."""
    try:
        # Verify chat session exists
        chat_session = get_chat_session(db, message.chat_session_id)
        if not chat_session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # Create AI message
        db_message = create_ai_message(
            db=db,
            chat_session_id=message.chat_session_id,
            content=message.content
        )
        return db_message
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat-sessions/{session_id}/ai-messages", response_model=AIMessageList)
def read_chat_ai_messages(session_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all AI messages for a chat session."""
    try:
        messages = get_chat_ai_messages(db, chat_session_id=session_id, skip=skip, limit=limit)
        return AIMessageList(messages=messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat-sessions/{session_id}/combined-messages", response_model=CombinedMessageList)
def read_combined_chat_messages(session_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all messages (both user and AI) for a chat session."""
    try: 
        # Verify chat session exists
        chat_session = get_chat_session(db, session_id)
        if not chat_session:
            raise HTTPException(status_code=404, detail="Chat session not found")    
        messages = get_combined_chat_messages(db, chat_session_id=session_id, skip=skip, limit=limit)
        return CombinedMessageList(messages=messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
