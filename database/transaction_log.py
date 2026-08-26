from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, func
from database.connections import Base


class Transaction(Base):
	__tablename__ = "transactions"

	id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
	account_id_from = Column(Integer, ForeignKey("accounts.id"), nullable=False)
	account_id_to = Column(Integer, ForeignKey("accounts.id"), nullable=False)
	amount = Column(Numeric(12, 2), nullable=False)
	transaction_date = Column(DateTime, nullable=False, server_default=func.now())


