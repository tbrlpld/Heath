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
    return testing.DummyRequest(dbsession=dbsession, **kwargs)
