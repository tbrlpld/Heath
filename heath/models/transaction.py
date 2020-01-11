# -*- coding: utf-8 -*-

"""Define Transaction model."""

from datetime import datetime

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Float,
    Text,
    DateTime,
)
from sqlalchemy.orm import relationship

from heath.models.meta import Base


class Transaction(Base):
    """
    Transaction class to represent financial transactions.

    Transactions can have a positive or negative amount (e.g. income vs.
    expenses).

    """

    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    amount = Column(
        Float(precision=2, decimal_return_scale=2),
        nullable=False,
    )

    account_id = Column(Integer, ForeignKey("accounts.id"))
    account = relationship("Account", back_populates="transactions")

    created = Column(DateTime, nullable=True, default=datetime.now)
