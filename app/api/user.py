from app.db.database import get_db
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import decode_access_token
from app.db.models import User
from fastapi import APIRouter
from app.core.redis_client import redis_client

oauth2_scheme = HTTPBearer()

router = APIRouter(prefix="/user", tags=["user"])

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    payload = decode_access_token(token.credentials)
    if payload is None or payload.get("sub") is None:
        raise credentials_exception
    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if user is None:
        raise credentials_exception
    

    key = f"user:{user.user_id}:auth_token"
    await  redis_client.set(key, token.credentials, ex=1800)
    if await  redis_client.exists(key):
        print("Token is stored in Redis.")
    return user


@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get the current user.
    """
    return current_user