from fastapi import APIRouter, Depends
from fastapi import Path
from sqlalchemy.orm import Session
from database.user_login_details import UserLogin
from dependencies.auth import get_authenticated_user
from service.accounts_service import get_account_details, get_all_accounts_details
from database.connections import get_db
from schemas.create_account_schema import AccountResponse

router = APIRouter()


@router.get("/accounts/{account_id}", response_model=AccountResponse, response_model_exclude_none=True)
def get_account(account_id: int = Path(..., gt=0), db: Session = Depends(get_db),current_user: UserLogin = Depends(get_authenticated_user)):
    return get_account_details(account_id, db,current_user)

@router.get("/accounts", response_model=list[AccountResponse], response_model_exclude_none=True)
def get_all_accounts(db: Session = Depends(get_db), current_user: UserLogin = Depends(get_authenticated_user)):
    return get_all_accounts_details(db,current_user)
