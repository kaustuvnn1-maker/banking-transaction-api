from decimal import Decimal

from pydantic import BaseModel, Field, field_validator,ConfigDict

class CreateAccount(BaseModel):
    account_holder_name:str
    balance: Decimal = Field(..., ge=Decimal("0"))

    @field_validator("account_holder_name")
    @classmethod
    def validate_account_holder_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("account_holder_name cannot contain only whitespace")
        return value 

class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, exclude_none=True)
    message: str | None = None
    account_id: int = Field(validation_alias="id")
    account_name: str = Field(validation_alias="account_holder_name")
    balance: Decimal