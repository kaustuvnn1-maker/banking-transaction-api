from decimal import Decimal
from pydantic import BaseModel, Field

class TransferDetails(BaseModel):
    from_account: int = Field(..., gt=0)
    to_account: int = Field(..., gt=0)
    amount: Decimal = Field(..., gt=Decimal("0"))
