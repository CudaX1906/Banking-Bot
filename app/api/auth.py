from ..schemas import UserCreate, UserOut, UserLogin
from app.db.database import get_db
from app.db.models import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import get_password_hash, verify_password, create_access_token
from app.api.user import get_current_user
from datetime import datetime

router = APIRouter()


@router.post("/register",status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, name=user.name, phone_number=user.phone_number, password=hashed_password, is_active=True)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully"}



@router.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    """
    Login a user and return the user object.
    """
    
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": db_user.email})
    

    return {"access_token": access_token, "token_type": "bearer", "user": db_user}

@router.post("/verify")
def verify(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Verify the user.
    """
    
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not active",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.user_id == current_user.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if user.phone_number is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User phone number is not set",
        )
    else:
        return {"message": "User is verified"}