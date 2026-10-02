from database.transaction_log import Transaction
from sqlalchemy.orm import Session
from database.accounts import Account
from database.user_login_details import UserLogin
from exceptions.business_exception import BusinessException
def get_all_transactions_log(current_user: UserLogin, db: Session):
    if current_user.role.lower() != "admin":
        raise BusinessException("Unauthorized access. Admin role required.", "UNAUTHORIZED", status_code=403)
    transaction_logs = db.query(Transaction).all()
    return transaction_logs

def get_all_transactions_by_id(db: Session, account_id: int,current_user: UserLogin):
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.userID,
    ).first()
    if not account:
        raise BusinessException("Account ID not found for this user.", "ACCOUNT_NOT_FOUND", status_code=404)
    transaction_logs = db.query(Transaction).filter(
        (Transaction.account_id_from == account_id) | (Transaction.account_id_to == account_id)
    ).all()
    return transaction_logs
