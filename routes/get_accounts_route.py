from fastapi import APIRouter, Depends
from fastapi import Path
from sqlalchemy.orm import Session
from service.accounts_service import get_account_details, get_all_accounts_details
from database.connections import get_db
from schemas.create_account_schema import AccountResponse

router = APIRouter()


@router.get("/accounts/{account_id}", response_model=AccountResponse)
def get_account(account_id: int = Path(..., gt=0), db: Session = Depends(get_db)):
    return get_account_details(account_id, db)

@router.get("/accounts", response_model=list[AccountResponse])
def get_all_accounts(db: Session = Depends(get_db)):
    return get_all_accounts_details(db)
