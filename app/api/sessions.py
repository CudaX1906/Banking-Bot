from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from datetime import datetime
from uuid import UUID
from typing import List
from app.db.database import get_db
from app.db.models import ChatSession as SessionModel, User,Message
from app.schemas import SessionOut
from app.db.schemas import SenderEnum
from app.api.user import get_current_user

router = APIRouter(prefix="/sessions", tags=["Sessions"])


def get_current_session(current_user: User = Depends(get_current_user), db: DBSession = Depends(get_db)) -> UUID:
    """
    Retrieve the current active session ID for the user.
    If no active session exists, raise an HTTPException.
    """
    session = db.query(SessionModel).filter_by(
        user_id=current_user.user_id,
        is_active=True
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="No active session found.")

    return session

@router.post("/initialize", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def initialize_new_session(
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Starts a new session whenever the user opens the bot.
    All previous sessions are marked as ended.
    """
    db.query(SessionModel).filter(
        SessionModel.user_id == current_user.user_id,
        SessionModel.is_active == True
    ).update({
        "is_active": False,
        "ended_at": datetime.utcnow()
    })

    new_session = SessionModel(user_id=current_user.user_id)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return new_session


@router.get("/active", response_model=SessionOut)
def get_active_session(
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the current active session for the user, if needed internally.
    """
    session = db.query(SessionModel).filter_by(
        user_id=current_user.user_id,
        is_active=True
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="No active session found.")
    
    return session

@router.get("/history", response_model=List[SessionOut])
def get_user_sessions(
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all past sessions of the user.
    """
    sessions = db.query(SessionModel).filter(
        SessionModel.user_id == current_user.user_id
    ).order_by(SessionModel.started_at.desc()).all()
    return sessions

@router.get("/messages/{session_id}", response_model=list[dict])
def get_messages(session_id: str, db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    
    session = db.query(SessionModel).filter(
        SessionModel.session_id == session_id,
        SessionModel.user_id == current_user.user_id
    ).first()

    if not session:
        raise HTTPException(status_code=403, detail="Session does not belong to the current user or does not exist.")

    messages = db.query(Message).filter(Message.session_id == session_id).order_by(Message.timestamp).all()
    if not messages:
        raise HTTPException(status_code=404, detail="No messages found for the given session ID")

    formatted_messages = [
        {"role": "user" if msg.sender == SenderEnum.user else "bot", "text": msg.content}
        for msg in messages
    ]

    return formatted_messages



@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    session = db.query(SessionModel).filter(
        SessionModel.session_id == session_id,
        SessionModel.user_id == current_user.user_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found or not owned by user")

    db.delete(session)
    db.commit()

    return