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

        self.errors: List[str] = []


    def to_dict(self) -> Dict:
        return self.__dict__

    # View Methods

    @view_config(
        route_name="accounts.add",
        renderer="heath:templates/accounts/add.jinja2",
        request_method="GET",
    )
    def add_get(self) -> Dict:
        return self.to_dict()

    @view_config(
        route_name="accounts.add",
        renderer="heath:templates/accounts/add.jinja2",
        request_method="POST",
    )
    def add_post(self) -> Union[Dict, HTTPFound]:
        # if self.validate_post_data():
        #     self.save_transaction()
        return HTTPFound(self.request.route_url("home"))


