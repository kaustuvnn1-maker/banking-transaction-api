from sqlalchemy.orm import Session
from schemas.create_new_user_schema import CreateNewUser
from service.user_creation import create_user_record

def new_user_creation(user: CreateNewUser, db: Session):
    user_record = create_user_record(db, user.username, user.password)
    return {"userID": user_record.userID, "username": user_record.username}