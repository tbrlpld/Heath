# -*- coding: utf-8 -*-

"""Define home view."""

from pyramid.view import view_config


@view_config(route_name='home', renderer='../templates/mytemplate.jinja2')
def home(request):
    return {}
