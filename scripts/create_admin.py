from database.connections import SessionLocal
from database.user_login_details import UserLogin
from pwdlib import PasswordHash
import os

password_hasher = PasswordHash.recommended()

db = SessionLocal()

username = os.getenv("ADMIN_USERNAME")
password = os.getenv("ADMIN_PASSWORD")

existing_user = (
    db.query(UserLogin)
    .filter(UserLogin.username == username)
    .first()
)

if existing_user:
    print("Admin already exists")
else:
    admin = UserLogin(
        username=username,
        password=password_hasher.hash(password),
        role="ADMIN"
    )

    db.add(admin)
    db.commit()

    print("Admin created")

db.close()