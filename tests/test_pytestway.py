# -*- coding: utf-8 -*-

"""Create tests in the pytest style."""

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

    return app


@pytest.fixture
def initialized_database(app):
    from heath.models.meta import Base
    Base.metadata.create_all(app.registry["engine"])


@pytest.fixture
def testapp(app, initialized_database):
    from webtest import TestApp
    testapp_instance = TestApp(app)

    return testapp_instance


@pytest.fixture
def example_data(app, initialized_database):
    session_factory = app.registry["dbsession_factory"]
    session = session_factory()

    from heath.models.transaction import Transaction
    first_transaction = Transaction(
        description="First transaction",
        amount=100.00,
    )
    second_transaction = Transaction(
        description="Second transaction",
        amount=-40.00,
    )
    session.add(first_transaction)
    session.add(second_transaction)
    session.commit()


def test_get_home(testapp):
    response = testapp.get("/")
    assert response.status_code == 200


def test_get_list(testapp, example_data):
    response = testapp.get("/list")
    assert response.status_code == 200


def test_for_links_in_list(testapp, example_data):
    response = testapp.get("/list")
    assert b'localhost/detail/1"' in response.body
    assert b'localhost/detail/2"' in response.body
