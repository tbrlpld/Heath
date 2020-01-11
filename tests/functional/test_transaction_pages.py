# -*- coding: utf-8 -*-

"""Functional tests for the transaction pages."""

import bs4
import pytest
import re

from tests.functional.conftest import HTML_PARSER


class TestTransactionCreateView(object):
    def test_get_create(self, testapp):
        response = testapp.get("/transactions/create")
        assert response.status_code == 200

        soup = bs4.BeautifulSoup(response.body, HTML_PARSER)
        assert soup.h1.text == "Create Transaction"
        forms = soup.select("form")
        assert len(forms) == 1
        description_input = soup.form.find("input", id="description")
        assert description_input["name"] == "description"
        amount_input = soup.form.find("input", id="amount")
        assert amount_input["name"] == "amount"
        assert amount_input["step"] == "0.01"

    def test_post_create(self, testapp):
        testapp.post(
            "/transactions/create",
            {
                "description": "A new transaction",
                "amount": "-99.99",
            },
            status=302,
        )

        # Check availability
        response = testapp.get("/transactions/1")
        assert response.status_code == 200
        assert "A new transaction" in response.text
        assert "-99.99" in response.text

    def test_post_invalid_amount(self, testapp):
        """Test posting invalid amount shows error message."""
        response = testapp.post(
            "/transactions/create",
            {
                "description": "A new transaction",
                "amount": "Not a number",
            },
            status=200,
        )

        soup = bs4.BeautifulSoup(response.text, HTML_PARSER)
        assert (soup.select("#errors")[0].li.text
                == "Amount has to be a number.")
        assert soup.find(id="description")["value"] == "A new transaction"
        assert soup.find(id="amount")["value"] == ""

    def test_submit_create_form(self, testapp):
        """Create a transaction by filling and submitting the form."""
        # Retrieve the form
        response = testapp.get(
            "/transactions/create",
            status=200,
        )
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
        soup = bs4.BeautifulSoup(response.body, HTML_PARSER)
        table = soup.find("table", id="transactions")
        transaction_cells = table.tbody.tr.find_all("td")
        assert "New Transaction" in transaction_cells[0].text
        assert "100" in transaction_cells[1].text


@pytest.fixture
def example_transactions(testapp):
    """Create example transaction for other views."""
    testapp.post(
        "/transactions/create",
        {
            "description": "First transaction",
            "amount": "100.00",
        },
        status=302,
    )
    testapp.post(
        "/transactions/create",
        {
            "description": "Second transaction",
            "amount": "-40.00",
        },
        status=302,
    )


class TestTransactionListView(object):
    def test_get_list(self, testapp):
        response = testapp.get(
            "/transactions/",
            status=200,
        )

    def test_for_links_in_list(self, testapp, example_transactions):
        response = testapp.get(
            "/transactions/",
            status=200,
        )

        soup = bs4.BeautifulSoup(response.body, HTML_PARSER)
        first_transaction_link = soup.find(href=re.compile("/transactions/1"))
        assert first_transaction_link is not None
        second_transaction_link = soup.find(href=re.compile("/transactions/2"))
        assert second_transaction_link is not None
        create_link = soup.find(href=re.compile("/transactions/create"))
        assert create_link is not None


class TestTransactionDetailView(object):
    """Test for the transaction detail view."""
    def test_404_when_not_exists(self, testapp):
        testapp.get("/transactions/1", status=404)

    def test_get_detail(self, testapp, example_transactions):
        testapp.get("/transactions/1", status=200)

    def test_detail_page_content(self, testapp, example_transactions):
        response = testapp.get("/transactions/1", status=200)

        soup = bs4.BeautifulSoup(response.body, HTML_PARSER)
        assert soup.find(id="description").text == "First transaction"
        assert soup.find(id="amount").text == "100.00"
        update_link = soup.find(href=re.compile("/transactions/1/update"))
        assert update_link.text == "Update"
        delete_link = soup.find(href=re.compile("/transactions/1/delete"))
        assert delete_link.text == "Delete"


class TestTransactionUpdateView(object):
    """Test for the transaction detail view."""
    def test_404_when_not_exists(self, testapp):
        testapp.get("/transactions/1/update", status=404)

    def test_get_update(self, testapp, example_transactions):
        testapp.get("/transactions/1/update", status=200)

    def test_update_page_content(self, testapp, example_transactions):
        response = testapp.get("/transactions/1/update", status=200)

        soup = bs4.BeautifulSoup(response.body, HTML_PARSER)
        assert "Update" in soup.h1.text
        assert soup.find(id="description")["value"] == "First transaction"
        assert soup.find(id="amount")["value"] == "100.00"
        cancel_link = soup.find(href=re.compile("/transactions/1"))
        assert cancel_link.text == "Cancel"

    def test_post_update_data(self, testapp, example_transactions):
        testapp.post(
            "/transactions/1/update",
            {
                "description": "New title",
                "amount": "99.99",
            },
            status=302,
        )

        # Change should be visible on detail.
        response = testapp.get("/transactions/1", status=200)
        soup = bs4.BeautifulSoup(response.body, HTML_PARSER)
        assert soup.find(id="description").text == "New title"
        assert soup.find(id="amount").text == "99.99"

    def test_post_update_with_invalid_amount(
        self,
        testapp,
        example_transactions,
    ):
        """Test invalid amount."""
        response = testapp.post(
            "/transactions/1/update",
            {
                "description": "New title",
                "amount": "Not a number",
            },
            status=200,
        )

        soup = bs4.BeautifulSoup(response.body, HTML_PARSER)
        # Input data is prefilled
        assert soup.find("input", id="description")["value"] == "New title"
        # The original value should be set back when the amount is invalid
        assert soup.find("input", id="amount")["value"] == "100.00"
        # Error message is shown
        error_element = soup.find(id="errors")
        assert error_element is not None
        assert "Amount has to be a number" in error_element.text

    def test_post_update_with_form(self, testapp, example_transactions):
        """Post with form."""
        # Retrieve the form
        response = testapp.get(
            "/transactions/1/update",
            status=200,
        )
        form = response.form
        # Fill the form
        form["description"] = "New Title"
        form["amount"] = "99.99"

        # Submit the form
        submit_response = form.submit("create")

        assert submit_response.status_code == 302
        # Redirect should be to list view and show the new data
        response = submit_response.follow()
        soup = bs4.BeautifulSoup(response.body, HTML_PARSER)
        table = soup.find("table", id="transactions")
        description_cell = table.tbody.find("td", text=re.compile("Title"))
        assert "New Title" in description_cell.text
        amount_cell = description_cell.find_next_sibling("td")
        assert "99.99" in amount_cell.text


class TestTransactionDeleteView(object):
    """Functional test for the transaction delete view."""
    def test_get_delete(self, testapp, example_transactions):
        response = testapp.get(
            "/transactions/1/delete",
            status=200,
        )

    def test_delete_page_content(self, testapp, example_transactions):
        response = testapp.get(
            "/transactions/1/delete",
            status=200,
        )

        soup = bs4.BeautifulSoup(response.body, HTML_PARSER)
        forms = soup.select("form")
        assert len(forms) == 1
        form = forms[0]
        assert form["method"] == "post"
        assert form["action"] == ""
        assert form.input["name"] == "delete.confirm"
        assert form.input["type"] == "submit"
        cancel_link = soup.find(href=re.compile("/transactions/1"))
        assert cancel_link.text == "Cancel"

    def test_post_no_data_to_delete_fails(self, testapp, example_transactions):
        """Posting no data to the view should fail."""
        testapp.post("/transactions/1/delete", status=400)

    def test_post_confirmation_delete_succeeds(
        self,
        testapp,
        example_transactions,
    ):
        """Posting `delete.confirm` to the endpoint should succeed."""
        testapp.post(
            "/transactions/1/delete",
            {"delete.confirm": "delete.confirm"},
            status=302,
        )

        # Check that detail is not available anymore
        testapp.get("/transactions/1", status=404)

    def test_form_functionality(self, testapp, example_transactions):
        """
        Test form functionality via WebTest.

        See also:
        https://docs.pylonsproject.org/projects/webtest/en/latest/forms.html#submit-a-form
        """

        # Get form
        response = testapp.get(
            "/transactions/1/delete",
            status=200,
        )
        form = response.form

        # Submitting the form
        response = form.submit("delete.confirm")

        assert response.status_code == 302
        # Check that detail is not available anymore
        testapp.get("/transactions/1", status=404)
