# -*- coding: utf-8 -*-

"""Define Account model."""

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
)
from sqlalchemy.orm import relationship

from heath.models.meta import Base


class Account(Base):
    """
    Account class that represents actual financial accounts.

    Transactions are associated with accounts to represent the actual splitting
    of financial transactions more accurately.
    """

    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False)

    transactions = relationship("Transaction", back_populates="account")

    created = Column(DateTime, nullable=True, default=datetime.now)
