# -*- coding: utf-8 -*-

"""Define views regarding transactions."""

from typing import Dict, Union

from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.sql import func


from heath.models.transaction import Transaction


@view_config(
    route_name="transaction.create",
    renderer="heath:templates/transactions/create.jinja2",
)
def create(request: Request) -> Dict:
    return_data: Dict = {}
    if request.method == "POST":
        try:
            amount = float(request.POST["amount"])
        except ValueError:
            return_data["errors"] = ["Amount has to be a number."]
            return_data["description"] = request.POST["description"]
            return_data["amount"] = request.POST["amount"]
            return return_data
        transaction = Transaction(
            description=request.POST["description"],
            amount=amount,
        )
        request.dbsession.add(transaction)
        return HTTPFound(request.route_url("transaction.list"))
    return return_data


@view_config(
    route_name="transaction.list",
    renderer="heath:templates/transactions/list.jinja2",
)
def transactions_list(request: Request) -> Dict:
    session = request.dbsession
    query = session.query(Transaction)
    transactions = query.order_by(Transaction.created.desc()).all()
    budget = session.query(func.sum(Transaction.amount)).scalar()
    return {
        "transactions": transactions,
        "budget": budget or 0.0,
    }


@view_config(
    route_name="transaction.detail",
    renderer="heath:templates/transactions/detail.jinja2",
)
def detail(request: Request) -> Dict:
    transaction_id = request.matchdict.get("transaction_id")

    session = request.dbsession
    transaction = session.query(Transaction).filter_by(
        id=transaction_id,
    ).first()

    if not transaction:
        raise HTTPNotFound()
    return {"transaction": transaction}


@view_config(
    route_name="transaction.update",
    renderer="heath:templates/transactions/edit.jinja2",
)
def update(request: Request) -> Dict:
    transaction_id = request.matchdict.get("transaction_id")
    dbsession = request.dbsession
    transaction = dbsession.query(Transaction).filter_by(
        id=transaction_id,
    ).first()
    if not transaction:
        raise HTTPNotFound()
    return_data = {"transaction": transaction}
    if request.method == "POST":
        try:
            transaction.amount = float(request.POST["amount"])
        except ValueError:
            return_data["errors"] = ["Amount has to be a number."]
            return_data["description"] = request.POST["description"]
            return_data["amount"] = request.POST["amount"]
            return return_data
        else:
            transaction.description = request.POST["description"]
            return HTTPFound(location="/transaction/")
    return return_data


@view_config(
    route_name="transaction.delete",
    renderer="heath:templates/transactions/delete.jinja2",
)
def delete(request: Request) -> Dict:
    transaction_id = request.matchdict.get("transaction_id")
    session = request.dbsession
    transaction = session.query(Transaction).filter_by(
        id=transaction_id,
    ).first()
    if not transaction:
        raise HTTPNotFound()
    if request.method == "POST":
        if "delete.confirm" in request.POST:
            session.delete(transaction)
            return HTTPFound(location="/transaction/")
        else:
            raise HTTPBadRequest()
    return {"transaction": transaction}
