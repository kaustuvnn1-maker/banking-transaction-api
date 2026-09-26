from sqlalchemy import Column, Integer, String

from database.connections import Base


class UserLogin(Base):
	__tablename__ = "userLogin"

	userID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
	username = Column(String, nullable=False, unique=True)
	password = Column(String, nullable=False)
