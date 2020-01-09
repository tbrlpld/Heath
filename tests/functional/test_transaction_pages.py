# -*- coding: utf-8 -*-

"""Functional tests for the transaction pages."""

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

    def test_post_invalid_amount(self, testapp):
        """Test posting invalid amount shows error message."""
        response = testapp.post(
            "/create",
            {
                "description": "A new transaction",
                "amount": "Not a number",
            },
            status=200,
        )

        soup = bs4.BeautifulSoup(response.text, "html.parser")
        assert (soup.select("#errors")[0].li.text
                == "Amount has to be a number.")
        assert soup.select("#description")[0]["value"] == "A new transaction"
        assert soup.select("#amount")[0]["value"] == "Not a number"

    def test_create_form(self, testapp):
        # Retrieve the form
        response = testapp.get("/create", status=200)
        form = response.form
        # Fill the form
        form["description"] = "New Transaction"
        form["amount"] = "100"
        # Submit the form
        submit_response = form.submit("create")
        assert submit_response.status_code == 302
        # Redirect should be to list view and contain the new transaction in
        # a table.
        response = submit_response.follow()
        soup = bs4.BeautifulSoup(response.body, "html.parser")
        table = soup.select("table#transactions")[0]
        transaction_cells = table.tbody.tr.find_all("td")
        assert "New Transaction" in transaction_cells[0].text
        assert "100" in transaction_cells[1].text


class TestListView(object):
    def test_get_list(self, testapp):
        response = testapp.get("/list")
        assert response.status_code == 200

    def test_for_links_in_list(self, testapp, example_data):
        response = testapp.get("/list")
        soup = bs4.BeautifulSoup(response.body, "html.parser")
        link_tags = soup.select("a")
        all_link_urls = [a["href"] for a in link_tags]
        all_link_url_string = " ".join(all_link_urls)
        assert "/detail/1" in all_link_url_string
        assert "/detail/2" in all_link_url_string
        assert "/create" in all_link_url_string


# TODO: Test  the detail view



# TODO: Test the edit view.
# TODO: Test invalid amount

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
