# -*- coding: utf-8 -*-

"""Define Transaction model."""

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    Float,
    Text,
    DateTime,
)

from .meta import Base


class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    amount = Column(
        Float(precision=2, decimal_return_scale=2),
        nullable=False,
    )

    created = Column(DateTime, nullable=True, default=datetime.now)
