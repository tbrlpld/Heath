# -*- coding: utf-8 -*-

"""Define views regarding transactions."""

from typing import Dict

from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config


@view_config(
    route_name="transaction_create",
    renderer="heath:templates/transactions/create.jinja2",
)
def create(request: Request) -> Dict:
    if request.method == "POST":
        print(request.POST)
        return {"message": "Transaction created"}
    return {}
