from database.user_login_details import UserLogin
from sqlalchemy.orm import Session
from schemas.create_new_user_schema import CreateNewUser
from exceptions.business_exception import BusinessException
from service.user_creation import create_user_record

def new_admin_creation(user: CreateNewUser, db: Session, current_user: UserLogin):
    if current_user.role.lower() != "admin":
        raise BusinessException("Unauthorized access. Admin role required.", "UNAUTHORIZED", status_code=403)

    user_record = create_user_record(db, user.username, user.password, role="admin")
    return {"userID": user_record.userID, "username": user_record.username}