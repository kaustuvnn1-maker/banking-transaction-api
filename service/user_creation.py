from pwdlib import PasswordHash
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database.user_login_details import UserLogin
from exceptions.business_exception import BusinessException


password_hasher = PasswordHash.recommended()


def create_user_record(
    db: Session,
    username: str,
    password: str,
    role: str | None = None,
) -> UserLogin:
    existing_user = db.query(UserLogin).filter(
        UserLogin.username == username,
    ).first()
    if existing_user:
        raise BusinessException(
            "Username already exists.",
            "USERNAME_ALREADY_EXISTS",
            status_code=409,
        )

    try:
        user_record = UserLogin(
            username=username,
            password=password_hasher.hash(password),
        )
        if role is not None:
            user_record.role = role
        db.add(user_record)
        db.commit()
        db.refresh(user_record)
        return user_record
    except SQLAlchemyError:
        db.rollback()
        raise