# -*- coding: utf-8 -*-

"""Define views regarding transactions."""

from typing import Dict, Union

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
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
        raise HTTPFound(location="/list")
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
        "budget": budget or 0.0,
    }


@view_config(
    route_name="transaction_detail",
    renderer="heath:templates/transactions/detail.jinja2",
)
def detail(request: Request) -> Dict:
    transaction_id = request.matchdict.get("transaction_id")

    session = request.dbsession
    transaction = session.query(Transaction).filter_by(id=transaction_id).first()

    if not transaction:
        raise HTTPNotFound()
    return {"transaction": transaction}


@view_config(
    route_name="transaction_edit",
    renderer="heath:templates/transactions/edit.jinja2",
)
def edit(request: Request) -> Dict:
    transaction_id = request.matchdict.get("transaction_id")
    session = request.dbsession
    transaction = session.query(Transaction).filter_by(
        id=transaction_id,
    ).first()
    if not transaction:
        raise HTTPNotFound()
    if request.method == "POST":
        transaction.description = request.POST["description"]
        transaction.amount = float(request.POST["amount"])
        raise HTTPFound(location="/list")
    return {"transaction": transaction}


@view_config(
    route_name="transaction_delete",
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
        session.delete(transaction)
        raise HTTPFound(location="/list")
    return {"transaction": transaction}
