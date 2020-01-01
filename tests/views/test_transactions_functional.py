# -*- coding: utf-8 -*-

"""Create tests in the pytest style. """

import bs4
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


class TestHome(object):
    def test_get_home(self, testapp):
        response = testapp.get("/")
        assert response.status_code == 200


class TestListView(object):
    def test_get_list(self, testapp):
        response = testapp.get("/list")
        assert response.status_code == 200

    def test_for_links_in_list(self, testapp, example_data):
        response = testapp.get("/list")
        assert b'localhost/detail/1"' in response.body
        assert b'localhost/detail/2"' in response.body
        assert b'localhost/create"' in response.body


class TestCreateView(object):
    def test_get_create(self, testapp):
        resp = testapp.get("/create")
        assert resp.status_code == 200
        assert b"Create Transaction" in resp.body
        assert b"<form" in resp.body
        assert b'name="description"' in resp.body
        assert b'name="amount"' in resp.body
        assert b'step="0.01"' in resp.body

    def test_post_create(self, testapp):
        testapp.post(
            "/create",
            {
                "description": "A new transaction",
                "amount": "-99.99",
            },
            status=302,
        )

        # Check availability
        response = testapp.get("/detail/1")
        assert response.status_code == 200
        assert "A new transaction" in response.text
        assert "-99.99" in response.text


class TestDeleteView(object):
    def test_get_delete(self, testapp, example_data):
        response = testapp.get("/delete/1")
        assert response.status_code == 200

        soup = bs4.BeautifulSoup(response.body, "html.parser")
        forms = soup.select("form")
        assert len(forms) == 1

        form = forms[0]
        assert form["method"] == "post"
        assert form["action"] == ""
        assert form.input["name"] == "delete.confirm"
        assert form.input["type"] == "submit"

    def test_post_delete_fail(self, testapp, example_data):
        """Posting no data to the view should fail."""
        testapp.post("/delete/1", status=400)

    def test_post_delete_success(self, testapp, example_data):
        """Posting `delete.confirm` to the endpoint should succeed."""
        testapp.post(
            "/delete/1",
            {"delete.confirm": "delete.confirm"},
            status=302,
        )
        # Check that detail is not available anymore
        testapp.get("/detail/1", status=404)

    # TODO: Test form availability and functionality
