#import time
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database.accounts import Account
from database.transaction_log import Transaction
from exceptions.business_exception import BusinessException
from schemas.transfer_schema import TransferDetails


def transfer_money(transfer_details: TransferDetails, db: Session, idem_key: str):
    if transfer_details.from_account == transfer_details.to_account:
        raise BusinessException("Cannot transfer to the same account.","SAME_ACCOUNT_TRANSFER")

    existing_transaction = db.query(Transaction).filter(
        Transaction.idem_key == idem_key,
    ).first()
    if existing_transaction:
        if (
            existing_transaction.account_id_from != transfer_details.from_account
            or existing_transaction.account_id_to != transfer_details.to_account
            or existing_transaction.amount != transfer_details.amount
        ):
            raise BusinessException(
                "Idempotency key has already been used for a different transfer.",
                "IDEM_KEY_REUSED",
                status_code=409,
            )
        return {
            "message": "Transfer already processed",
            "from_account": existing_transaction.account_id_from,
            "to_account": existing_transaction.account_id_to,
        }
    try:
        from_account = db.query(Account).filter(
            Account.id == transfer_details.from_account
        ).with_for_update().first()
        to_account = db.query(Account).filter(
            Account.id == transfer_details.to_account
        ).with_for_update().first()
        if not from_account:
            raise BusinessException("From Account not found.", "ACCOUNT_FROM_NOT_FOUND",status_code=404)
        if not to_account:
            raise BusinessException("To Account not found.", "ACCOUNT_TO_NOT_FOUND",status_code=404)

        if from_account.balance < transfer_details.amount:
            raise BusinessException("Insufficient balance.", "INSUFFICIENT_BALANCE")

    
        from_account.balance -= transfer_details.amount
        # Introduce error here to test rollback
        #raise RuntimeError("Intentional error for rollback testing")
        to_account.balance += transfer_details.amount
        #raise RuntimeError("Intentional error for rollback testing")
        #time.sleep(8)
        db.add(Transaction(
            account_id_from=transfer_details.from_account,
            account_id_to=transfer_details.to_account,
            amount=transfer_details.amount,
            transaction_status="SUCCESS",
            idem_key=idem_key,
        ))
        db.commit()
        return {"message": "Transfer successful", "from_account": transfer_details.from_account, "to_account": transfer_details.to_account}
    except IntegrityError:
        db.rollback()
        existing_transaction = db.query(Transaction).filter(
            Transaction.idem_key == idem_key,
        ).first()
        if existing_transaction:
            if (
                existing_transaction.account_id_from != transfer_details.from_account
                or existing_transaction.account_id_to != transfer_details.to_account
                or existing_transaction.amount != transfer_details.amount
            ):
                raise BusinessException(
                    "Idempotency key has already been used for a different transfer.",
                    "IDEM_KEY_REUSED",
                    status_code=409,
                )
            return {
                "message": "Transfer already processed",
                "from_account": existing_transaction.account_id_from,
                "to_account": existing_transaction.account_id_to,
            }
        raise
    except Exception:
        db.rollback()
        raise
