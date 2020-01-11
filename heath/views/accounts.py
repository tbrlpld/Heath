# -*- coding: utf-8 -*-

"""Define views regarding accounts."""

from typing import Dict, List, Optional, Union

from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from pyramid.request import Request
from pyramid.view import view_config
from sqlalchemy.sql import func
from sqlalchemy.orm import Session

from heath.models.account import Account


class AccountViews(object):
    """View class for transaction views."""

    def __init__(self, request: Request):
        self.request: Request = request
        self.dbsession: Session = self.request.dbsession

        self.name: str

        self.errors: List[str] = []

    def validate_post_data(self):
        """
        Validate the post data.

        Extracts the required data from the post request and saved the values
        into the corresponding attributes.

        Returns:
            bool: True if post data is valid, False otherwise.

        Raises:
            HTTPBadRequest: Raised if keys are missing. So far only "name" is
                required.

        """
        name = self.request.POST.get("name", None)
        if name is None:
            raise HTTPBadRequest()
        if name == "":
            self.errors.append("Name can not be empty.")
            return False
        else:
            self.name = name
            return True

    def save_account(self):
        """Save account from the current view state."""
        account = Account()
        account.name = self.name
        self.request.dbsession.add(account)

    def to_dict(self) -> Dict:
        return self.__dict__

    # View Methods

    @view_config(
        route_name="accounts.create",
        renderer="heath:templates/accounts/create.jinja2",
        request_method="GET",
    )
    def create_get(self) -> Dict:
        return self.to_dict()

    @view_config(
        route_name="accounts.create",
        renderer="heath:templates/accounts/create.jinja2",
        request_method="POST",
    )
    def create_post(self) -> Union[Dict, HTTPFound]:
        if self.validate_post_data():
            self.save_account()
            return HTTPFound(self.request.route_url("home"))
        return self.to_dict()


