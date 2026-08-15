from fastapi import APIRouter
from service.get_account_logic import get_account_details
router = APIRouter()

@router.get("/accounts/{account_id}")
def get_account(account_id: int):
    return get_account_details(account_id)