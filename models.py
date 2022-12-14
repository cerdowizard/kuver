import enum
import uuid
from datetime import datetime

from sqlalchemy.orm import relationship

from database.database import Base
from sqlalchemy import TIMESTAMP, Column, String, Boolean, text, Enum, ForeignKey, DateTime, func,Integer
from sqlalchemy.dialects.postgresql import UUID


# class Roles(str, enum.Enum):
#     Admin = "admin"
#     User = "user"

class Roles(str, enum.Enum):
    Admin = "admin"
    SuperAdmin = "superadmin"
    User = "user"

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)
    first_name = Column(String(256), nullable=False)
    last_name = Column(String(256), nullable=False)
    username = Column(String(101), unique=True, nullable=False)
    email = Column(String(256), unique=True, nullable=False)
    password = Column(String(256), nullable=False)
    country = Column(String(256), nullable=False)
    mobile_number = Column(String(256), nullable=False)
    verified = Column(Boolean, nullable=False, server_default='True')
    role = Column(Enum(Roles), default=Roles.User)
    # transaction = relationship("Transaction", back_populates="owner", cascade="all,delete")
    created_at = Column(DateTime(), default=func.now())
    updated_at = Column(DateTime(), onupdate=datetime.now())


class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)
    # user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    receivers_name = Column(String(256), nullable=False)
    receivers_accNumber = Column(Integer, nullable=False)
    Currency_from = Column(String(256), nullable=False)
    Currency_to = Column(String(256), nullable=False)
    amount_send = Column(Integer, nullable=False)
    amount_received = Column(Integer, nullable=False)
    status = Column(String(256), server_default='pending', nullable=False)
    # owner = relationship("User", back_populates="transaction")
    created_at = Column(DateTime(), default=func.now())
    updated_at = Column(DateTime(), onupdate=datetime.now())


class Currency(Base):
    __tablename__ = 'currencies'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)
    country = Column(String(256), nullable=False)
    currency_name = Column(String(256), nullable=False)
    currency_price = Column(Integer, nullable=False)
    created_at = Column(DateTime(), default=func.now())
    updated_at = Column(DateTime(), onupdate=datetime.now())


class Reset_Token(Base):
    __tablename__ = "reset_token"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)
    email = Column(String(256), nullable=False)
    token = Column(String(256), nullable=False)
    created_at = Column(DateTime(), default=func.now())
    updated_at = Column(DateTime(), onupdate=datetime.now())
