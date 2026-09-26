from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from database.accounts import Account  # noqa: F401
from database.transaction_log import Transaction  # noqa: F401
from exceptions.business_exception import BusinessException
from middleware.request_middleware import RequestLoggingMiddleware
from routes.create_account_route import create_account_router  # noqa: F401
from routes.get_accounts_route import router as accounts_router
from routes.get_transactions_route import get_transaction_router  # noqa: F401
from routes.login_user_route import login_router
from routes.new_user_creation_route import create_user_router
from routes.transfer_route import router as transfer_router

app = FastAPI()
app.add_middleware(RequestLoggingMiddleware)

@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "detail": exc.message},
    )


app.include_router(transfer_router)
app.include_router(accounts_router)
app.include_router(create_account_router)
app.include_router(get_transaction_router)
app.include_router(create_user_router)
app.include_router(login_router)

@app.get("/health")
def get_health():
    return {"status": "ok"}


