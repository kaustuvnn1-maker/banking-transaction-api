from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.connections import get_db
from schemas.transfer_schema import TransferDetails, TransferResponse
from service.transfer_service import transfer_money

router = APIRouter()


@router.post("/transfers", response_model=TransferResponse)
def money_transfer(transfer_details: TransferDetails,db: Session = Depends(get_db)):
    return transfer_money(transfer_details,db)
