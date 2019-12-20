# -*- coding: utf-8 -*-

"""Define views regarding transactions."""

from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config


@view_config(
    route_name="transaction_create",
    renderer="../templates/transactions/create.jinja2",
)
def create(request: Request) -> Response:
    return {}
