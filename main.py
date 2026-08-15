from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from exceptions.business_exception import BusinessException
from routes.get_accounts_route import router as accounts_router
from routes.transfer_route import router as transfer_router

app = FastAPI()


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


@app.get("/health")
def get_health():
    return {"status": "ok"}


