from sqlalchemy.orm import Session
from app.db.models import Account
from app.exceptions import AccountNotFound

class AccountService:
    
    @staticmethod
    def get_account_details(account_id: str, db: Session):
        """
        Get the account details for a given account ID.
        """
        account = db.query(Account).filter(Account.account_id == account_id).first()
        if not account:
            raise AccountNotFound(f"Account with ID {account_id} not found.")
        return {
            "account_id": account.account_id,
            "balance": account.balance,
            "account_type": account.account_type,
            "currency": account.currency,
            "account_number": account.account_number,
        }
    
    @staticmethod
    def update_account_details(account_id: str, details: dict, db: Session):
        """
        Update the account details for a given account ID.
        """
        account = db.query(Account).filter(Account.account_id == account_id).first()
        if not account:
            raise AccountNotFound(f"Account with ID {account_id} not found.")
        
        for key, value in details.items():
            setattr(account, key, value)
        
        db.commit()
        db.refresh(account)
        
        return {
            "account_id": account.account_id,
            "balance": account.balance,
            "account_type": account.account_type,
            "currency": account.currency,
            "account_number": account.account_number,
        }
    
    @staticmethod
    def close_account(account_id: str, db: Session):
        """
        Close the account for a given account ID.
        """
        account = db.query(Account).filter(Account.account_id == account_id).first()
        if not account:
            raise AccountNotFound(f"Account with ID {account_id} not found.")
        
        db.delete(account)
        db.commit()
        
        return {"message": f"Account with ID {account_id} has been closed."}
    
    @staticmethod
    def create_account(account_data: dict, db: Session):
        """
        Create a new account.
        """
        import uuid 
        generated_account_number = str(uuid.uuid4().int)[0:12]  # Example: 12-digit unique number

        new_account = Account(
            **account_data,
            account_number=generated_account_number,
        )
        db.add(new_account)
        db.commit()
        db.refresh(new_account)

        return {
            "account_id": new_account.account_id,
            "balance": new_account.balance,
            "account_type": new_account.account_type,
            "currency": new_account.currency,
            "account_number": new_account.account_number,
        }

