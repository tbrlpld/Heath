# -*- coding: utf-8 -*-

"""Define views regarding transactions."""

from typing import Dict

from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config

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
