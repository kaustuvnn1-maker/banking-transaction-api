from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.create_new_user_schema import CreateNewUser
from service.create_user import new_user_creation
from database.connections import get_db
from schemas.create_account_schema import AccountResponse

create_user_router = APIRouter()

@create_user_router.post("/auth/register")
def create_user(user: CreateNewUser, db: Session = Depends(get_db)):
    return new_user_creation(user,db)
