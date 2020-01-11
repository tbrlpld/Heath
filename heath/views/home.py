# -*- coding: utf-8 -*-

"""Define home view."""

from pyramid.view import view_config

from heath.models.account import Account


@view_config(route_name='home', renderer='../templates/home.jinja2')
def home(request):
    accounts = request.dbsession.query(Account).all()
    return {"accounts": accounts}
