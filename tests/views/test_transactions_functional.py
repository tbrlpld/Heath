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


class TestCreateView(object):
    def test_get_create(self, testapp):
        response = testapp.get("/create")
        assert response.status_code == 200

        soup = bs4.BeautifulSoup(response.body, "html.parser")
        assert soup.h1.text == "Create Transaction"
        forms = soup.select("form")
        assert len(forms) == 1
        description_input = soup.form.select("input#description")[0]
        assert description_input["name"] == "description"
        amount_input = soup.form.select("input#amount")[0]
        assert amount_input["name"] == "amount"
        assert amount_input["step"] == "0.01"

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


class TestListView(object):
    def test_get_list(self, testapp):
        response = testapp.get("/list")
        assert response.status_code == 200

    def test_for_links_in_list(self, testapp, example_data):
        response = testapp.get("/list")
        assert b'localhost/detail/1"' in response.body
        assert b'localhost/detail/2"' in response.body
        assert b'localhost/create"' in response.body


# TODO: Add tests for the detail view



# Add functional tests to the edit view.

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

    def test_form_functionality(self, testapp, example_data):
        """
        Test form functionality via WebTest.

        See also:
        https://docs.pylonsproject.org/projects/webtest/en/latest/forms.html#submit-a-form
        """

        # Get form
        response = testapp.get("/delete/1", status=200)
        form = response.form
        # Submitting the form
        response = form.submit("delete.confirm")
        assert response.status_code == 302
        # Check that detail is not available anymore
        testapp.get("/detail/1", status=404)
