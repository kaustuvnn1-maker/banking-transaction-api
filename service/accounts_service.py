from database.user_login_details import UserLogin
from exceptions.business_exception import BusinessException
from database.accounts import Account
from sqlalchemy.orm import Session

def get_account_details(account_id: int, db: Session,current_user: UserLogin):
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.userID,
    ).first()
    if not account:
        raise BusinessException("Account not found for this user.", "ACCOUNT_NOT_EXISTS", status_code=404)
    return account

def get_all_accounts_details(db: Session,current_user: UserLogin): 
    if current_user.role.lower() != "admin":
        raise BusinessException("Unauthorized access. Admin role required.", "UNAUTHORIZED", status_code=403)
    accounts = db.query(Account).all()
    return accounts