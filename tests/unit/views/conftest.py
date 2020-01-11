# -*- coding: utf-8 -*-

"""Shared pytest fixtures for the view tests."""

import pytest
from pyramid import testing
import transaction  # this is not my module, but a package for transaction management


@pytest.fixture
def dbsession_for_unittest():
    config = testing.setUp(settings={
        'sqlalchemy.url': 'sqlite:///:memory:',
    })
    config.include('heath.models')
    settings = config.get_settings()

    from heath.models import (
        get_engine,
        get_session_factory,
        get_tm_session,
    )

    engine = get_engine(settings)

    from heath.models.meta import Base
    Base.metadata.create_all(engine)

    dbsession_factory = get_session_factory(engine)
    dbsession = get_tm_session(dbsession_factory, transaction.manager)

    yield dbsession

    testing.tearDown()
    transaction.abort()
    Base.metadata.drop_all(engine)


def dummy_request(dbsession, **kwargs):
    dummy_request = testing.DummyRequest(dbsession=dbsession, **kwargs)
    # Make route_url function always return a slash. This is to prevent
    # look up errors when trying to generate URLs from route names.
    # Because during unit testing of the view functions there is no app context
    # and the route configuration is not known during test. Therefore, the
    # lookup has to fail. By adding this "mock" function the route lookup
    # will always return a valid path.
    dummy_request.route_url = lambda *_, **__: "/"
    return dummy_request


@pytest.fixture
def dummy_get_request(dbsession_for_unittest):
    """Return a dummy request with the dbsession attached to it."""
    return dummy_request(dbsession=dbsession_for_unittest)


@pytest.fixture
def dummy_post_request(dbsession_for_unittest):
    """Return a dummy request with empty payload the dbsession attached."""
    return dummy_request(dbsession=dbsession_for_unittest, post={})
