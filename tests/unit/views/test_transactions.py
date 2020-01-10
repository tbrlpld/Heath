# -*- coding: utf-8 -*-

"""Unit tests for the transaction views."""

import pytest

from tests.unit.views.conftest import dummy_request


@pytest.fixture
def example_transactions(dbsession_for_unittest):
    session = dbsession_for_unittest
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
    return (
        first_transaction,
        second_transaction,
    )


@pytest.fixture
def dummy_get_request(dbsession_for_unittest):
    """Return a dummy request with the dbsession attached to it."""
    return dummy_request(dbsession=dbsession_for_unittest)


@pytest.fixture
def dummy_post_request(dbsession_for_unittest):
    """Return a dummy request with empty payload the dbsession attached."""
    return dummy_request(dbsession=dbsession_for_unittest, post={})


class TestTransactionCreateView(object):
    """Test for the create view."""

    @pytest.fixture
    def dummy_post_create_request(
        self,
        dummy_post_request,
    ):
        """Create dummy post request with payload for new transaction."""
        dummy_post_request.POST = {
            "description": "New Transaction",
            "amount": 100.00,
        }
        return dummy_post_request

    def test_empty_response_when_request_wo_payload(
        self,
        dummy_get_request,
    ):
        from heath.views.transactions import TransactionView
        response = TransactionView(dummy_get_request).create()

        assert response == {}

    def test_redirect_after_successful_creation(
        self,
        dummy_post_create_request,
    ):
        from heath.views.transactions import TransactionView
        from pyramid.httpexceptions import HTTPFound

        response = TransactionView(dummy_post_create_request).create()
        assert isinstance(response, HTTPFound)

    def test_creation_in_db(
        self,
        dummy_post_create_request,
        dbsession_for_unittest,
    ):
        from heath.views.transactions import TransactionView
        from pyramid.httpexceptions import HTTPFound

        response = TransactionView(dummy_post_create_request).create()

        # Verify creation in database
        from heath.models.transaction import Transaction
        first_transaction = dbsession_for_unittest.query(Transaction).first()
        assert first_transaction.id == 1
        assert first_transaction.description == "New Transaction"
        assert first_transaction.amount == 100.00

    def test_negative_amount_works(
        self,
        dummy_post_create_request,
        dbsession_for_unittest,
    ):
        request = dummy_post_create_request
        request.POST["amount"] = -100.00

        from heath.views.transactions import TransactionView
        response = TransactionView(request).create()

        # Redirect after successful creation
        from pyramid.httpexceptions import HTTPFound
        assert isinstance(response, HTTPFound)
        # Verify creation in database
        from heath.models.transaction import Transaction
        first_transaction = dbsession_for_unittest.query(Transaction).first()
        assert first_transaction.id == 1
        assert first_transaction.description == "New Transaction"
        assert first_transaction.amount == -100.00

    def test_invalid_amount_leads_to_error_message(
        self,
        dummy_post_create_request,
        dbsession_for_unittest,
    ):
        """Test handling when amount is not a number."""
        request = dummy_post_create_request
        request.POST["amount"] = "Not a number"

        from heath.views.transactions import TransactionView
        response = TransactionView(request).create()

        assert response["errors"][0] == "Amount has to be a number."
        assert response["description"] == "New Transaction"
        assert response["amount"] == "Not a number"
        # Verify no creation in database
        from heath.models.transaction import Transaction
        first_transaction = dbsession_for_unittest.query(Transaction).first()
        assert first_transaction is None

    # TODO: Test empty description leads to error message
    # TODO: Test empty amount leads to error message


class TestTransactionListView(object):
    """Unit tests for transaction list view."""

    def test_returns_empty_list_when_no_transactions(
        self,
        dummy_get_request,
    ):
        """Return empty transactions list."""
        from heath.views.transactions import TransactionView
        response = TransactionView(dummy_get_request).list()

        assert response["transactions"] == []

    def test_zero_budget_when_no_transactions(
        self,
        dummy_get_request,
    ):
        """Return zero budget when no transactions exist."""
        from heath.views.transactions import TransactionView
        response = TransactionView(dummy_get_request).list()

        assert response["budget"] == 0.0

    def test_all_transactions_returned(
        self,
        dummy_get_request,
        example_transactions,
    ):
        from heath.views.transactions import TransactionView
        response = TransactionView(dummy_get_request).list()

        assert "transactions" in response
        assert example_transactions[0] in response["transactions"]
        assert example_transactions[1] in response["transactions"]

    def test_transactions_in_reverse_order(
        self,
        dummy_get_request,
        example_transactions,
    ):
        from heath.views.transactions import TransactionView
        response = TransactionView(dummy_get_request).list()

        # Test order of transactions (last transaction is first in list)
        assert example_transactions[-1] == response["transactions"][0]
        assert example_transactions[0] == response["transactions"][-1]

    def test_transaction_sum(
        self,
        dummy_get_request,
        example_transactions,
    ):
        # Add test for remaining budget returned
        from heath.views.transactions import TransactionView
        response = TransactionView(dummy_get_request).list()

        assert response["budget"] == 60.0


class TestTransactionDetailView(object):
    """Tests for the transaction detail view."""

    def test_404_when_not_existing(
        self,
        dummy_get_request,
    ):
        dummy_get_request.matchdict["transaction_id"] = 1

        from pyramid.httpexceptions import HTTPNotFound
        from heath.views.transactions import TransactionView
        with pytest.raises(HTTPNotFound):
            TransactionView(dummy_get_request).detail()

    def test_return_one_transaction(
        self,
        dummy_get_request,
        example_transactions,
    ):
        dummy_get_request.matchdict["transaction_id"] = 1

        from heath.views.transactions import TransactionView
        response = TransactionView(dummy_get_request).detail()

        assert "transaction" in response
        assert response["transaction"].id == 1
        assert response["transaction"].description == "First transaction"
        assert response["transaction"].amount == 100.00


class TestTransactionUpdateView(object):
    """Unit tests for the transaction edit view."""

    @pytest.fixture
    def dummy_post_update_request(
        self,
        dummy_post_request,
    ):
        post_request = dummy_post_request
        post_request.POST = {
            "description": "New Title",
            "amount": 123.00,
        }
        post_request.matchdict["transaction_id"] = 1
        return post_request

    def test_404_when_requesting_not_existing_id(
        self,
        dummy_get_request,
    ):
        """Test for get to not existing id."""
        dummy_get_request.matchdict["transactions_id"] = 1

        from heath.views.transactions import TransactionView
        from pyramid.httpexceptions import HTTPNotFound
        with pytest.raises(HTTPNotFound):
            TransactionView(dummy_get_request).update()

    def test_return_transaction_on_get(
        self,
        dummy_get_request,
        example_transactions,
    ):
        dummy_get_request.matchdict["transaction_id"] = 1

        from heath.views.transactions import TransactionView
        response = TransactionView(dummy_get_request).update()

        assert "transaction" in response
        assert response["transaction"].id == 1
        assert response["transaction"].description == "First transaction"
        assert response["transaction"].amount == 100.00

    def test_post_updates_information_in_db(
        self,
        dummy_post_update_request,
        example_transactions,
        dbsession_for_unittest,
    ):
        from heath.views.transactions import TransactionView
        TransactionView(dummy_post_update_request).update()

        # Check persistence in database
        from heath.models.transaction import Transaction
        first_transaction = dbsession_for_unittest.query(Transaction).first()
        assert first_transaction.id == 1
        assert first_transaction.description == "New Title"
        assert first_transaction.amount == 123.00

    def test_redirect_after_successful_update(
        self,
        dummy_post_update_request,
        example_transactions,
    ):
        from heath.views.transactions import TransactionView
        response = TransactionView(dummy_post_update_request).update()

        from pyramid.httpexceptions import HTTPFound
        assert isinstance(response, HTTPFound)

    def test_invalid_amount_leads_to_error_message(
        self,
        dummy_post_update_request,
        example_transactions,
        dbsession_for_unittest,
    ):
        """Test handling when amount is not a number."""
        dummy_post_update_request.POST["amount"] = "Not a number"

        from heath.views.transactions import TransactionView
        response = TransactionView(dummy_post_update_request).update()

        # Data is returned into the form
        assert response["errors"][0] == "Amount has to be a number."
        assert response["description"] == "New Title"
        assert response["amount"] == "Not a number"
        # The database content is not updated.
        from heath.models.transaction import Transaction
        first_transaction = dbsession_for_unittest.query(Transaction).first()
        assert first_transaction.description == "First transaction"
        assert first_transaction.amount == 100.00

    # TODO: Test empty description leads to error message
    # TODO: Test empty amount leads to error message


class TestTransactionDeleteView(object):
    """Unit tests for the transaction delete view."""

    def test_404_requesting_not_existing_id(
        self,
        dummy_get_request,
    ):
        dummy_get_request.matchdict["transaction_id"] = 1

        from pyramid.httpexceptions import HTTPNotFound
        from heath.views.transactions import TransactionView
        with pytest.raises(HTTPNotFound):
            TransactionView(dummy_get_request).delete()

    def test_return_transaction_when_post_wo_payload(
        self,
        dummy_get_request,
        example_transactions,
    ):
        dummy_get_request.matchdict["transaction_id"] = 1

        from heath.views.transactions import TransactionView
        response = TransactionView(dummy_get_request).delete()

        assert "transaction" in response
        assert response["transaction"].id == 1
        assert response["transaction"].description == "First transaction"
        assert response["transaction"].amount == 100.00

    # Require deletion confirmation to be set in post.
    # This is just a little extra requirement to prevent posts to the delete
    # endpoints resulting automatically in deletion of the objects
    # Empty posts should not delete an object.
    def test_empty_post_leads_to_bad_reqeust(
        self,
        dummy_post_request,
        example_transactions,
    ):
        dummy_post_request.matchdict["transaction_id"] = 1

        from heath.views.transactions import TransactionView
        from pyramid.httpexceptions import HTTPBadRequest
        with pytest.raises(HTTPBadRequest):
            TransactionView(dummy_post_request).delete()

    def test_empty_post_not_deleteting_transaction(
        self,
        dummy_post_request,
        example_transactions,
        dbsession_for_unittest,
    ):
        dummy_post_request.matchdict["transaction_id"] = 1

        from pyramid.httpexceptions import HTTPBadRequest
        from heath.views.transactions import TransactionView
        # Exception needs to be caught to not fail the test
        with pytest.raises(HTTPBadRequest):
            TransactionView(dummy_post_request).delete()

        # Check that transaction still exists
        from heath.models.transaction import Transaction
        first_transaction = dbsession_for_unittest.query(
            Transaction,
        ).filter_by(id=1).first()
        assert first_transaction == example_transactions[0]

    def test_post_confirmation_deletes_transaction(
        self,
        dummy_post_request,
        example_transactions,
        dbsession_for_unittest,
    ):
        dummy_post_request.POST["delete.confirm"] = "delete.confirm"
        dummy_post_request.matchdict["transaction_id"] = 1

        from heath.views.transactions import TransactionView
        TransactionView(dummy_post_request).delete()

        # Check persistence in database
        from heath.models.transaction import Transaction
        first_transaction = dbsession_for_unittest.query(
            Transaction,
        ).filter_by(id=1).first()
        assert first_transaction == None

    def test_redirect_after_successful_deletion(
        self,
        dummy_post_request,
        example_transactions,
    ):
        dummy_post_request.POST["delete.confirm"] = "delete.confirm"
        dummy_post_request.matchdict["transaction_id"] = 1

        from heath.views.transactions import TransactionView
        response = TransactionView(dummy_post_request).delete()

        from pyramid.httpexceptions import HTTPFound
        assert isinstance(response, HTTPFound)
