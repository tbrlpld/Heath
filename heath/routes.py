# -*- coding: utf-8 -*-

"""Define routes of the application."""


def transaction_routes(config):
    """Define only transaction related routes."""
    config.add_route('transaction.create', '/create')
    config.add_route('transaction.list', '/')
    config.add_route('transaction.detail', '/{transaction_id}')
    config.add_route('transaction.update', '/{transaction_id}/update')
    config.add_route('transaction.delete', '/{transaction_id}/delete')


def includeme(config):
    """Pull route configuration together."""
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')

    config.include(transaction_routes, route_prefix="/transaction/")
