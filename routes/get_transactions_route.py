from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connections import get_db
from database.user_login_details import UserLogin
from dependencies.auth import get_authenticated_user
from service.get_transaction_service import get_all_transactions_log
from service.get_transaction_service import get_all_transactions_by_id
from fastapi import Path
from schemas.transaction_schema import TransactionResponse
get_transaction_router = APIRouter()

@get_transaction_router.get("/transactions", response_model=list[TransactionResponse])
def get_transactions(db: Session = Depends(get_db),current_user: UserLogin = Depends(get_authenticated_user)):
    return get_all_transactions_log(current_user,db)

@get_transaction_router.get("/accounts/{account_id}/transactions", response_model=list[TransactionResponse])
def get_history_by_id(db:Session = Depends(get_db), account_id:  int = Path(..., gt=0), current_user: UserLogin = Depends(get_authenticated_user)):
    return get_all_transactions_by_id(db, account_id,current_user) 