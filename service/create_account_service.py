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
        return {"message": "Account created successfully", "account": account_record}
    except SQLAlchemyError:
        db.rollback()
        raise