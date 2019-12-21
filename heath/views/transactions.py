# -*- coding: utf-8 -*-

"""Define views regarding transactions."""

from typing import Dict

from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.sql import func

from heath.models.transaction import Transaction


@view_config(
    route_name="transaction_create",
    renderer="heath:templates/transactions/create.jinja2",
)
def create(request: Request) -> Dict:
    if request.method == "POST":
        transaction = Transaction(
            description=request.POST["description"],
            amount=float(request.POST["amount"]),
        )
        session = request.dbsession
        session.add(transaction)
        return {"message": "Transaction created"}
    return {}


@view_config(
    route_name="transactions_list",
    renderer="heath:templates/transactions/list.jinja2",
)
def transactions_list(request: Request) -> Dict:
    session = request.dbsession
    query = session.query(Transaction)
    transactions = query.order_by(Transaction.created.desc()).all()
    budget = session.query(func.sum(Transaction.amount)).scalar()
    return {
        "transactions": transactions,
        "budget": budget,
    }
