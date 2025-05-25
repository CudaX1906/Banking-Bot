from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from datetime import datetime
from uuid import UUID

from app.db.database import get_db
from app.db.models import ChatSession as SessionModel, User
from app.schemas import SessionOut
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
