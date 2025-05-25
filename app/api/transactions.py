from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas import TransactionCreate, TransactionOut
from app.services.transaction_service import TransactionService
from app.db.models import User
from app.api.user import get_current_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/create", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction_data: TransactionCreate, db: Session = Depends(get_db),current_user: User = Depends(get_current_user),):
    """
    Initiate a new transaction after balance validation.
    """
    try:
        return TransactionService.create_transaction(transaction_data, db)
    except HTTPException as e:
        raise e


@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(transaction_id: str, db: Session = Depends(get_db),current_user: User = Depends(get_current_user),):
    """
    Fetch details of a specific transaction.
    """
    return TransactionService.get_transaction_by_id(transaction_id, db)


@router.get("/account/{account_number}", response_model=list[TransactionOut])
def get_transactions_by_account(account_number: str, db: Session = Depends(get_db),current_user: User = Depends(get_current_user),):
    """
    Fetch all transactions for a given account.
    """
    return TransactionService.list_transactions_by_account(account_number, db)
