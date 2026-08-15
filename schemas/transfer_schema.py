from pydantic import BaseModel, Field
class TransferDetails(BaseModel):
    from_account: int = Field(..., gt=0)
    to_account: int = Field(..., gt=0)
    amount: float = Field(..., gt=0)
