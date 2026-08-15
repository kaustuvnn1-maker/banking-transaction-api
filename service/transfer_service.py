from schemas.transfer_schema import TransferDetails


def transfer_money(transfer_details: TransferDetails):
    return {
        "from_account": transfer_details.from_account,
        "to_account": transfer_details.to_account,
        "amount": transfer_details.amount,
        "status": "success",
    }
