# app/api/fallback_help.py

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import FallbackHelpRequest, User,ChatSession
from app.schemas import FallbackHelpRequestInput, FallbackHelpRequestOut
from .user import get_current_user  # assumes you're using this
from uuid import UUID
from app.api.sessions import get_current_session

router = APIRouter(prefix="/support", tags=["Support Requests"])



@router.post("/", response_model=FallbackHelpRequestOut, status_code=status.HTTP_201_CREATED)
def create_fallback_help_request(
    help_input: FallbackHelpRequestInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    session: ChatSession = Depends(get_current_session),
):
    """
    Create a support request for the current user and session.
    """
    help_request = FallbackHelpRequest(
        user_id=current_user.user_id,
        session_id=session.session_id,
        notes=help_input.notes
    )
    db.add(help_request)
    db.commit()
    db.refresh(help_request)
    return help_request
