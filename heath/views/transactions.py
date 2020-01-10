# -*- coding: utf-8 -*-

"""Define views regarding transactions."""

from typing import Dict, List

from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from pyramid.request import Request
from pyramid.view import view_config
from sqlalchemy.sql import func

from heath.models.transaction import Transaction


class TransactionView(object):
    """View class for transaction views."""

    def __init__(self, request: Request):
        self.request: Request = request
        self.dbsession = self.request.dbsession

        self.errors: List[str] = []

    def get_post_data(self):
        """Save the values from POST to view object."""
        self.description = self.request.POST.get("description")
        self.amount = self.request.POST.get("amount")

    def validate_data(self) -> bool:
        """Validate data. Return True or False. Set error message."""
        try:
            self.amount = float(self.amount)
        except (ValueError, TypeError):
            self.errors.append("Amount has to be a number.")
            return False
        return True

    def save_transaction(self):
        transaction = Transaction(
            description=self.description,
            amount=self.amount,
        )
        self.dbsession.add(transaction)

    def to_dict(self):
        return self.__dict__

    # View Methods

    @view_config(
        route_name="transaction.create",
        renderer="heath:templates/transactions/create.jinja2",
    )
    def create(self) -> Dict:
        if self.request.method == "POST":
            self.get_post_data()
            if self.validate_data():
                self.save_transaction()
                return HTTPFound(self.request.route_url("transaction.list"))
        return self.to_dict()

    @view_config(
        route_name="transaction.list",
        renderer="heath:templates/transactions/list.jinja2",
    )
    def list(self) -> Dict:
        dbsession = self.request.dbsession
        query = dbsession.query(Transaction)
        transactions = query.order_by(Transaction.created.desc()).all()
        budget = dbsession.query(func.sum(Transaction.amount)).scalar()
        return {
            "transactions": transactions,
            "budget": budget or 0.0,
        }


    @view_config(
        route_name="transaction.detail",
        renderer="heath:templates/transactions/detail.jinja2",
    )
    def detail(self) -> Dict:
        transaction_id = self.request.matchdict.get("transaction_id")

        transaction = self.request.dbsession.query(Transaction).filter_by(
            id=transaction_id,
        ).first()

        if not transaction:
            raise HTTPNotFound()
        return {"transaction": transaction}


    @view_config(
        route_name="transaction.update",
        renderer="heath:templates/transactions/edit.jinja2",
    )
    def update(self) -> Dict:
        transaction_id = self.request.matchdict.get("transaction_id")
        dbsession = self.request.dbsession
        transaction = dbsession.query(Transaction).filter_by(
            id=transaction_id,
        ).first()
        if transaction is None:
            raise HTTPNotFound()

        return_data = {"transaction": transaction}
        if self.request.method == "POST":
            description = self.request.POST.get("description", "")
            amount = self.request.POST.get("amount", "")
            if description and amount:
                try:
                    transaction.amount = float(amount)
                except ValueError:
                    return_data["errors"] = ["Amount has to be a number."]
                    return_data["description"] = description
                    return_data["amount"] = amount
                    return return_data
                else:
                    transaction.description = description
                    return HTTPFound(self.request.route_url("transaction.list"))
        return return_data


    @view_config(
        route_name="transaction.delete",
        renderer="heath:templates/transactions/delete.jinja2",
    )
    def delete(self) -> Dict:
        transaction_id = self.request.matchdict.get("transaction_id")
        dbsession = self.request.dbsession
        transaction = dbsession.query(Transaction).filter_by(
            id=transaction_id,
        ).first()
        if not transaction:
            raise HTTPNotFound()
        if self.request.method == "POST":
            if "delete.confirm" in self.request.POST:
                dbsession.delete(transaction)
                return HTTPFound(self.request.route_url("transaction.list"))
            else:
                raise HTTPBadRequest()
        return {"transaction": transaction}
