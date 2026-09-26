from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.create_new_user_schema import CreateNewUser as loginUser
from service.login_user_service import login_user_verification
from database.connections import get_db

login_router = APIRouter()

@login_router.post("/auth/login")
def login_user(user: loginUser, db: Session = Depends(get_db)):
    return login_user_verification(user,db)
