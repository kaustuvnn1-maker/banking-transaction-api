from database.user_login_details import UserLogin
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from schemas.create_new_user_schema import CreateNewUser
from pwdlib import PasswordHash
from exceptions.business_exception import BusinessException


password_hasher = PasswordHash.recommended()

def new_user_creation(user: CreateNewUser, db: Session):
    existing_user = db.query(UserLogin).filter(
        UserLogin.username == user.username,
    ).first()
    if existing_user:
        raise BusinessException(
            "Username already exists.",
            "USERNAME_ALREADY_EXISTS",
            status_code=409,
        )

    try:
        user_record = UserLogin(
            username=user.username,
            password=password_hasher.hash(user.password),
            role=user.role
        )
        db.add(user_record)
        db.commit()
        db.refresh(user_record)
        return {"userID": user_record.userID, "username": user_record.username, "role": user_record.role}
    except SQLAlchemyError:
        db.rollback()
        raise