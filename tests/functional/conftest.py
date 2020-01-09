# -*- coding: utf-8 -*-

"""Shared pytest fixtures for the view tests."""

import pytest
from pyramid import testing


@pytest.fixture
def app():
    config = testing.setUp(settings={
        'sqlalchemy.url': 'sqlite:///:memory:',
    })
    settings = config.get_settings()

    from heath import main
    app = main({}, **settings)

    yield app

    testing.tearDown()


@pytest.fixture
def initialized_database(app):
    engine = app.registry["engine"]
    from heath.models.meta import Base
    Base.metadata.create_all(engine)

    yield

    Base.metadata.drop_all(engine)


@pytest.fixture
def testapp(app, initialized_database):
    from webtest import TestApp
    testapp_instance = TestApp(app)

    return testapp_instance
