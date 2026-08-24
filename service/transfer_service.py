from sqlalchemy.orm import Session
from database.accounts import Account
from exceptions.business_exception import BusinessException
from schemas.transfer_schema import TransferDetails


def transfer_money(transfer_details: TransferDetails,db: Session):
    if transfer_details.from_account == transfer_details.to_account:
        raise BusinessException("Cannot transfer to the same account.","SAME_ACCOUNT_TRANSFER")
    from_account = db.query(Account).filter(Account.id == transfer_details.from_account).first()
    to_account = db.query(Account).filter(Account.id == transfer_details.to_account).first()

    if not from_account:
        raise BusinessException("From Account not found.", "ACCOUNT_FROM_NOT_FOUND",status_code=404)
    if not to_account:
        raise BusinessException("To Account not found.", "ACCOUNT_TO_NOT_FOUND",status_code=404)

    if from_account.balance < transfer_details.amount:
        raise BusinessException("Insufficient balance.", "INSUFFICIENT_BALANCE")

    try:
        from_account.balance -= transfer_details.amount
        # Introduce error here to test rollback
        #raise RuntimeError("Intentional error for rollback testing")
        to_account.balance += transfer_details.amount
        db.commit()
        return {"message": "Transfer successful", "from_account": transfer_details.from_account, "to_account": transfer_details.to_account}
    except Exception:
        db.rollback()
        raise
