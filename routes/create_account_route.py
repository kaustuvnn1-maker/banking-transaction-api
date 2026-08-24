from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.create_account_schema import CreateAccount
from service.create_account_service import new_account_creation
from database.connections import get_db

create_account_router = APIRouter()

@create_account_router.post("/accounts")
def create_account(account: CreateAccount,db: Session = Depends(get_db)):
    return new_account_creation(account,db)
