from pydantic import BaseModel


class TransferDetails(BaseModel):
    from_account: int
    to_account: int
    amount: float
