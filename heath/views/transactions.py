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
        self.transactions: Optional[List[Transaction]] = None
        self.budget: float
        self.transaction: Optional[Transaction] = None
        self.description: str
        self.amount: Optional[float] = None
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

    def validate_post_data(self) -> bool:
        """Validate data. Return True or False. Set error message."""
        self.description = self.request.POST.get("description", "")
        try:
            self.amount = float(self.request.POST.get("amount", ""))
        except (ValueError, TypeError):
            self.errors.append("Amount has to be a number.")
            return False
        return True

    def save_transaction(self):
        """Save transaction with the current data."""
        if self.transaction is None:
            self.transaction = Transaction()
        self.transaction.description = self.description
        self.transaction.amount = self.amount
        self.dbsession.add(self.transaction)

    def confirmed_deletion(self) -> bool:
        """Delete if confirmed. Return info if deletion happened."""
        if "delete.confirm" in self.request.POST:
            self.dbsession.delete(self.transaction)
            return True
        return False

    def to_dict(self) -> Dict:
        return self.__dict__

    # View Methods

    @view_config(
        route_name="transaction.create",
        renderer="heath:templates/transactions/create.jinja2",
        request_method="GET",
    )
    def create_get(self) -> Dict:
        return self.to_dict()

    @view_config(
        route_name="transaction.create",
        renderer="heath:templates/transactions/create.jinja2",
        request_method="POST",
    )
    def create_post(self) -> Union[Dict, HTTPFound]:
        if self.validate_post_data():
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
        self.get_transactions()
        if not self.transaction:
            raise HTTPNotFound()

        if self.request.method == "POST":
            if self.validate_post_data():
                self.save_transaction()
                return HTTPFound(self.request.route_url("transaction.list"))
        return self.to_dict()


    @view_config(
        route_name="transaction.delete",
        renderer="heath:templates/transactions/delete.jinja2",
    )
    def delete(self) -> Dict:
        self.get_transactions()
        if not self.transaction:
            raise HTTPNotFound()

        if self.request.method == "POST":
            if self.confirmed_deletion():
                return HTTPFound(self.request.route_url("transaction.list"))
            else:
                raise HTTPBadRequest()
        return self.to_dict()
