from sqlalchemy import Column, Integer, String

from database import Base


class Status:
    RECEIVED: int = 0
    CONFIRMED: int = 1


class User(Base):
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    firstname = Column(String)
    lastname = Column(String)
    email = Column(String)
    created = Column(Integer)


class Friends(Base):
    __tablename__ = 'Friends'

    requesting_user_name = Column(String, primary_key=True)
    receiving_user_name = Column(String, primary_key=True)
    status = Column(Integer, default=Status.RECEIVED)
    created = Column(Integer)
