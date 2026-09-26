from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.connections import get_db
from database.user_login_details import UserLogin
from dependencies.auth import get_authenticated_user
from schemas.create_account_schema import AccountResponse, CreateAccount
from service.create_account_service import new_account_creation

create_account_router = APIRouter()


@create_account_router.post("/accounts", response_model=AccountResponse, response_model_exclude_none=True)
def create_account(
    account: CreateAccount,
    db: Session = Depends(get_db),
    current_user: UserLogin = Depends(get_authenticated_user),
):
    return new_account_creation(account, db,current_user)
