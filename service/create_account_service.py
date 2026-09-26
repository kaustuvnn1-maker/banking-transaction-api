from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database.accounts import Account
from schemas.create_account_schema import CreateAccount


def new_account_creation(account: CreateAccount, db: Session,current_user):
    try:
        account_record = Account(**account.model_dump())
        account_record.user_id = current_user.userID
        db.add(account_record)
        db.commit()
        db.refresh(account_record)
        return account_record
    except SQLAlchemyError:
        db.rollback()
        raise