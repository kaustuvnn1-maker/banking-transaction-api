from exceptions.business_exception import BusinessException
from schemas.transfer_schema import TransferDetails


def transfer_money(transfer_details: TransferDetails):
    if transfer_details.from_account == transfer_details.to_account:
        raise BusinessException("Cannot transfer to the same account.","SAME_ACCOUNT_TRANSFER")

    return {
        "from_account": transfer_details.from_account,
        "to_account": transfer_details.to_account,
        "amount": transfer_details.amount,
        "status": "success",
    }
