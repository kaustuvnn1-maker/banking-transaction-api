from database.accounts import Account
from schemas.create_account_schema import CreateAccount
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

def new_account_creation(account: CreateAccount, db: Session):
    try:
        account_record = Account(**account.model_dump())
        db.add(account_record)
        db.commit()
        db.refresh(account_record)
        return account_record
        # return {
        #         "message": "Account created successfully",
        #         "account_id": account_record.id,
        #         "account_name": account_record.account_holder_name,
        #         "balance": account_record.balance,
        #     }
    except SQLAlchemyError:
        db.rollback()
        raise