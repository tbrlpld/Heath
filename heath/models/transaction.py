from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    Text,
)

from .meta import Base


class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    amount = Column(Numeric(precision=2), nullable=False)
