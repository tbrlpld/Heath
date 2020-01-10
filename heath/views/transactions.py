# -*- coding: utf-8 -*-

"""Define views regarding transactions."""

from typing import Dict, List, Optional, Union

from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from pyramid.request import Request
from pyramid.view import view_config
from sqlalchemy.sql import func
from sqlalchemy.orm import Session

from heath.models.transaction import Transaction


class TransactionView(object):
    """View class for transaction views."""

    def __init__(self, request: Request):
        self.request: Request = request
        self.dbsession: Session = self.request.dbsession

        self.transaction_id: str = self.request.matchdict.get(
            "transaction_id",
            "",
        )
        self.transactions: List[Transaction]
        self.budget: float
        self.transaction: Transaction
        self.description: str
        self.amount: Optional[float]

        self.errors: List[str] = []

    def get_transactions(self):
        """
        Get one or all transactions.

        If a transaction id is retrieved from the request, set the
        `transaction` (notice the singular) to the corresponding `Transaction`
        object.

        If no transaction id is retrieved from the request, set the
        `transactions` (notice the plural) attribute to a list containing all
        transactions.
        """
        if self.transaction_id:
            self.transaction: Transaction = self.dbsession.query(
                Transaction,
            ).filter_by(
                id=self.transaction_id,
            ).first()
        else:
            self.transactions: List[Transaction] = self.dbsession.query(
                Transaction,
            ).order_by(
                Transaction.created.desc(),
            ).all()


    def get_budget(self):
        retrieved_budget = self.dbsession.query(
            func.sum(Transaction.amount),
        ).scalar()
        self.budget = retrieved_budget or 0.0

    def get_post_data(self):
        """Save the values from POST to view object."""
        self.description = self.request.POST.get("description", "")
        self.amount = self.request.POST.get("amount", "")

    def validate_data(self) -> bool:
        """Validate data. Return True or False. Set error message."""
        try:
            self.amount = float(self.amount)
        except (ValueError, TypeError):
            self.errors.append("Amount has to be a number.")
            return False
        return True

    def save_transaction(self):
        transaction: Transaction = Transaction(
            description=self.description,
            amount=self.amount,
        )
        self.dbsession.add(transaction)

    def to_dict(self) -> Dict:
        return self.__dict__

    # View Methods

    @view_config(
        route_name="transaction.create",
        renderer="heath:templates/transactions/create.jinja2",
    )
    def create(self) -> Union[Dict, HTTPFound]:
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
        self.get_transactions()
        self.get_budget()
        return self.to_dict()

    @view_config(
        route_name="transaction.detail",
        renderer="heath:templates/transactions/detail.jinja2",
    )
    def detail(self) -> Dict:
        self.get_transactions()
        if not self.transaction:
            raise HTTPNotFound()
        return self.to_dict()

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
