from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    account_id_from: int
    account_id_to: int
    amount: Decimal
    transaction_date: datetime
