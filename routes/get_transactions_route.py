from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connections import get_db
from service.get_transaction_service import get_all_transactions_log
from service.get_transaction_service import get_all_transactions_by_id
from fastapi import Path
get_transaction_router = APIRouter()

@get_transaction_router.get("/transactions")
def get_transactions(db: Session = Depends(get_db)):
    return get_all_transactions_log(db)

@get_transaction_router.get("/accounts/{account_id}/transactions")
def get_history_by_id(db:Session = Depends(get_db), account_id:  int = Path(..., gt=0)):
    return get_all_transactions_by_id(db, account_id)