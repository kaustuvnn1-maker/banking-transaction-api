import os
from datetime import datetime, timedelta, timezone

import jwt
from database.user_login_details import UserLogin
from sqlalchemy.orm import Session
from schemas.create_new_user_schema import CreateNewUser as loginUser
from pwdlib import PasswordHash
from exceptions.business_exception import BusinessException


password_hasher = PasswordHash.recommended()

def login_user_verification(user: loginUser, db: Session):
    existing_user = db.query(UserLogin).filter(
        UserLogin.username == user.username,
    ).first()
    if not existing_user:
        raise BusinessException(
            "Invalid username or password.",
            "INVALID_CREDENTIALS",
            status_code=401,
        )

    if not password_hasher.verify(user.password, existing_user.password):
        raise BusinessException(
            "Invalid username or password.",
            "INVALID_CREDENTIALS",
            status_code=401,
        )

    secret_key = os.getenv("JWT_SECRET_KEY")
    if not secret_key:
        raise RuntimeError("JWT_SECRET_KEY must be configured to issue login tokens.")

    now = datetime.now(timezone.utc)
    access_token = jwt.encode(
        {
            "sub": str(existing_user.userID),
            "username": existing_user.username,
            "iat": now,
            "exp": now + timedelta(minutes=30),
        },
        secret_key,
        algorithm="HS256",
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
    }