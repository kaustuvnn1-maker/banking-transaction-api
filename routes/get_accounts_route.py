from fastapi import APIRouter
from fastapi import Path
router = APIRouter()
@router.get("/accounts/{account_id}")
def get_account(account_id: int = Path(..., gt=0)):
    return {
        "account_id": account_id,
        "account_name": "John Doe",
        "balance": 1000.0
    }