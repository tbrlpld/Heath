# -*- coding: utf-8 -*-

"""Define home view."""

from pyramid.view import view_config


@view_config(route_name='landing', renderer='../templates/landing.jinja2')
def landing(request):
    return {}
