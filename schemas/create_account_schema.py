from pydantic import BaseModel, Field, field_validator

class CreateAccount(BaseModel):
    account_holder_name:str
    balance: float = Field(..., ge=0)

    @field_validator("account_holder_name")
    @classmethod
    def validate_account_holder_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("account_holder_name cannot contain only whitespace")
        return value