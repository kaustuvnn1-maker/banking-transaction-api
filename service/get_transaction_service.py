from database.transaction_log import Transaction
from sqlalchemy.orm import Session
from database.accounts import Account
from exceptions.business_exception import BusinessException
def get_all_transactions_log(db: Session):
    transaction_logs = db.query(Transaction).all()
    return transaction_logs
    # logs = []
    # for log in transaction_logs:
    #     logs.append({
    #         "id": log.id,
    #         "account_id_from": log.account_id_from,
    #         "account_id_to": log.account_id_to,
    #         "amount": float(log.amount),
    #         "transaction_date": log.transaction_date.isoformat(),
    #     })
    # return logs

def get_all_transactions_by_id(db: Session, account_id: int):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise BusinessException("Account not found.", "ACCOUNT_NOT_FOUND", status_code=404)
    transaction_logs = db.query(Transaction).filter(
        (Transaction.account_id_from == account_id) | (Transaction.account_id_to == account_id)
    ).all()
    return transaction_logs
    # logs = []
    
    # for log in transaction_logs:
    #     logs.append({
    #         "id": log.id,
    #         "account_id_from": log.account_id_from,
    #         "account_id_to": log.account_id_to,
    #         "amount": float(log.amount),
    #         "transaction_date": log.transaction_date.isoformat(),
    #     })
    # return logs
