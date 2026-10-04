from database.user_login_details import UserLogin
from exceptions.business_exception import BusinessException
from database.accounts import Account
from sqlalchemy.orm import Session

def get_account_details(account_id: int, db: Session,current_user: UserLogin):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise BusinessException("Account not found.", "ACCOUNT_NOT_EXISTS", status_code=404)
    if account.user_id != current_user.userID:
        raise BusinessException("You do not own this account.", "ACCOUNT_NOT_OWNED_BY_USER", status_code=403)
    return account

def get_all_accounts_details(db: Session,current_user: UserLogin): 
    accounts_query = db.query(Account)
    if current_user.role.lower() != "admin":
        accounts_query = accounts_query.filter(Account.user_id == current_user.userID)
    return accounts_query.all()