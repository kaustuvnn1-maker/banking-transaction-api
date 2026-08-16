from exceptions.business_exception import BusinessException
from database.accounts import Account
from sqlalchemy.orm import Session

def get_account_details(account_id: int, db: Session):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise BusinessException("Account not found","ACCOUNT_NOT_EXISTS", status_code=404)
    return {
        "account_id": account_id,
        "account_name": account.account_holder_name,
        "balance": float(account.balance),
    }

def get_all_accounts_details(db: Session): 
    accounts = db.query(Account).all()
    all_accounts = []
    for account in accounts:
        all_accounts.append({
            "account_id": account.id,
            "account_name": account.account_holder_name,
            "balance": float(account.balance),
        })
    return all_accounts