from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/health")
def get_health():
    return {"status": "ok"}


@app.get("/accounts/{account_id}")
def get_account(account_id: int):
    return {
        "account_id": account_id,
        "account_holder": "Alice",
        "balance": 10000,
    }


class TransferDetails(BaseModel):
    from_account: int
    to_account: int
    amount: float 
 

@app.post("/transfers")
def money_transfer(transfer_details: TransferDetails):
    return {
        "from_account": transfer_details.from_account,
        "to_account": transfer_details.to_account,
        "amount": transfer_details.amount,
        "status": "success",
    }
