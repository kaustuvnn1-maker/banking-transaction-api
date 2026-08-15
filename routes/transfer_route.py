from fastapi import APIRouter

from schemas.transfer_schema import TransferDetails
from service.transfer_service import transfer_money

router = APIRouter()


@router.post("/transfers")
def money_transfer(transfer_details: TransferDetails):
    return transfer_money(transfer_details)
