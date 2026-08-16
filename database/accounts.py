from sqlalchemy import Column, Integer, String, Numeric
from database.connections import Base


class Account(Base):
	__tablename__ = "accounts"

	id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
	account_holder_name = Column(String, nullable=False)
	balance = Column(Numeric(12, 2), nullable=False)


