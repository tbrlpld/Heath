# -*- coding: utf-8 -*-

"""Create tests in the pytest style."""

import pytest


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


def test_get_list(testapp):
    response = testapp.get("/list")
    assert response.status_code == 200


def test_for_links_in_list(testapp, example_data):
    response = testapp.get("/list")
    assert b'localhost/detail/1"' in response.body
    assert b'localhost/detail/2"' in response.body
    assert b'localhost/create"' in response.body


def test_get_create(testapp):
    resp = testapp.get("/create")
    assert resp.status_code == 200
    assert b"Create Transaction" in resp.body
    assert b"<form" in resp.body
    assert b'name="description"' in resp.body
    assert b'name="amount"' in resp.body
    assert b'step="0.01"' in resp.body

# TODO: Add test post to create
