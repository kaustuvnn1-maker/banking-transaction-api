from fastapi import FastAPI

from routes.get_accounts_route import router as accounts_router
from routes.transfer_route import router as transfer_router

app = FastAPI()

app.include_router(transfer_router)
app.include_router(accounts_router)


@app.get("/health")
def get_health():
    return {"status": "ok"}


