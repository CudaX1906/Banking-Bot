from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, Account
from app.schemas import AccountInfo, AccountUpdate, AccountCreate
from app.services.account_service import AccountService
from .user import get_current_user

router = APIRouter(prefix="/account", tags=["account"])

@router.get("/info", response_model=AccountInfo, status_code=status.HTTP_200_OK)
async def get_account_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get account information for the current user.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=401, detail="User is not active")

    account = db.query(Account).filter(
        Account.user_id == current_user.user_id,
        Account.is_active == True
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Active account not found for user")

    return AccountService.get_account_details(account.account_id, db)

@router.put("/update", response_model=AccountInfo, status_code=status.HTTP_200_OK)
async def update_account_info(
    account_info: AccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update account information for the current user.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=401, detail="User is not active")

    account = db.query(Account).filter(
        Account.user_id == current_user.user_id,
        Account.is_active == True
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Active account not found for user")

    return AccountService.update_account_details(account.account_id, account_info.dict(exclude_unset=True), db)

@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete (deactivate) account for the current user.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=401, detail="User is not active")

    account = db.query(Account).filter(
        Account.user_id == current_user.user_id,
        Account.is_active == True
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Active account not found for user")

    AccountService.close_account(account.account_id, db)
    return {"detail": "Account deleted successfully"}

@router.post("/create", response_model=AccountInfo, status_code=status.HTTP_201_CREATED)
async def create_account(
    account_data: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new account for the current user with a minimum balance requirement.
    """
    MINIMUM_INITIAL_BALANCE = 100.0  # Minimum initial balance requirement

    if account_data.balance < MINIMUM_INITIAL_BALANCE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Minimum initial balance must be at least ${MINIMUM_INITIAL_BALANCE}",
        )

    new_account_data = account_data.dict()
    new_account_data["user_id"] = current_user.user_id
    new_account_data["is_active"] = True

    return AccountService.create_account(new_account_data, db)
