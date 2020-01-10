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
def dummy_request_with_dbsession(dbsession_for_unittest):
    """Return a dummy request with the dbsession attached to it."""
    return dummy_request(dbsession=dbsession_for_unittest)


class TestTransactionCreateView(object):
    """Test for the create view."""

    def test_create_view(self, dbsession_for_unittest):
        from heath.views.transactions import TransactionView

        response = TransactionView(
            dummy_request(dbsession_for_unittest),
        ).create()
        assert response == {}

    @pytest.fixture
    def dummy_post_request(self, dbsession_for_unittest):
        """Create dummy post request with payload for new transaction."""
        return dummy_request(
            dbsession=dbsession_for_unittest,
            post={
                "description": "New Transaction",
                "amount": 100.00,
            },
        )

    def test_redirect_after_successful_creation(self, dummy_post_request):
        from heath.views.transactions import TransactionView
        from pyramid.httpexceptions import HTTPFound

        response = TransactionView(dummy_post_request).create()
        assert isinstance(response, HTTPFound)

    def test_post_to_create_view(
        self,
        dbsession_for_unittest,
        dummy_post_request,
    ):
        from heath.views.transactions import TransactionView
        from pyramid.httpexceptions import HTTPFound

        response = TransactionView(dummy_post_request).create()
        assert isinstance(response, HTTPFound)

        # Verify creation in database
        session = dbsession_for_unittest
        from heath.models.transaction import Transaction
        first_transaction = session.query(Transaction).first()
        assert first_transaction.id == 1
        assert first_transaction.description == "New Transaction"
        assert first_transaction.amount == 100.00

    def test_negative_amount(self, dbsession_for_unittest):
        session = dbsession_for_unittest
        request = dummy_request(
            dbsession=session,
            post={
                "description": "New Transaction",
                "amount": -100.00,
            },
        )

        from heath.views.transactions import TransactionView
        from pyramid.httpexceptions import HTTPFound
        response = TransactionView(request).create()
        assert isinstance(response, HTTPFound)

        # Verify creation in database
        from heath.models.transaction import Transaction
        first_transaction = session.query(Transaction).first()
        assert first_transaction.id == 1
        assert first_transaction.description == "New Transaction"
        assert first_transaction.amount == -100.00

    def test_invalid_amount(self, dbsession_for_unittest):
        """Test handling when amount is not a number."""
        session = dbsession_for_unittest
        request = dummy_request(
            dbsession=session,
            post={
                "description": "New Transaction",
                "amount": "Not a number",
            },
        )

        from heath.views.transactions import TransactionView
        response = TransactionView(request).create()

        assert response["errors"][0] == "Amount has to be a number."
        assert response["description"] == "New Transaction"
        assert response["amount"] == "Not a number"
        # Verify no creation in database
        from heath.models.transaction import Transaction
        first_transaction = session.query(Transaction).first()
        assert first_transaction is None


class TestTransactionListView(object):
    """Unit tests for transaction list view."""

    def test_zero_budget(self, dummy_request_with_dbsession):
        """Return zero buget when no transactions exist."""
        from heath.views.transactions import TransactionView
        response = TransactionView(dummy_request_with_dbsession).list()

        assert response["budget"] == 0.0

    def test_empty_transactios_list(self, dummy_request_with_dbsession):
        """Return empty transactions list."""
        from heath.views.transactions import TransactionView
        response = TransactionView(dummy_request_with_dbsession).list()

        assert response["transactions"] == []

    def test_all_transactions_returned(
        self,
        example_transactions,
        dummy_request_with_dbsession,
    ):
        from heath.views.transactions import TransactionView
        response = TransactionView(dummy_request_with_dbsession).list()

        assert "transactions" in response
        assert example_transactions[0] in response["transactions"]
        assert example_transactions[1] in response["transactions"]

    def test_transactions_in_reverse_order(
        self,
        example_transactions,
        dummy_request_with_dbsession,
    ):
        # Test order of transactions (last transaction first in list)
        from heath.views.transactions import TransactionView
        response = TransactionView(dummy_request_with_dbsession).list()

        assert example_transactions[-1] == response["transactions"][0]
        assert example_transactions[0] == response["transactions"][-1]

    def test_transaction_sum(
        self,
        example_transactions,
        dummy_request_with_dbsession,
    ):
        # Add test for remaining budget returned
        from heath.views.transactions import TransactionView
        response = TransactionView(dummy_request_with_dbsession).list()

        assert response["budget"] == 60.0


class TestTransactionDetailView(object):
    """Tests for the transaction detail view."""

    def test_show_only_one_transaction(
        self,
        dummy_request_with_dbsession,
        example_transactions,
    ):
        request = dummy_request_with_dbsession
        request.matchdict["transaction_id"] = 1

        from heath.views.transactions import TransactionView
        response = TransactionView(request).detail()

        assert "transaction" in response
        assert response["transaction"].id == 1
        assert response["transaction"].description == "First transaction"
        assert response["transaction"].amount == 100.00

    def test_404_when_not_existing(
        self,
        dummy_request_with_dbsession,
    ):
        request = dummy_request_with_dbsession
        request.matchdict["transaction_id"] = 1

        from pyramid.httpexceptions import HTTPNotFound
        from heath.views.transactions import TransactionView
        with pytest.raises(HTTPNotFound):
            TransactionView(request).detail()


class TestTransactionUpdateView(object):
    """Unit tests for the transaction edit view."""

    def test_show_only_one_transaction(
        self,
        dummy_request_with_dbsession,
        example_transactions,
    ):
        request = dummy_request_with_dbsession
        request.matchdict["transaction_id"] = 1

        from heath.views.transactions import TransactionView
        response = TransactionView(request).update()

        assert "transaction" in response
        assert response["transaction"].id == 1
        assert response["transaction"].description == "First transaction"
        assert response["transaction"].amount == 100.00

    def test_404_when_not_existing(self, dummy_request_with_dbsession):
        request = dummy_request_with_dbsession
        request.matchdict["transaction_id"] = 1

        from pyramid.httpexceptions import HTTPNotFound
        from heath.views.transactions import TransactionView
        with pytest.raises(HTTPNotFound):
            TransactionView(request).update()

    @pytest.fixture
    def update_post_request(self, dbsession_for_unittest):
        post_request = dummy_request(
            dbsession=dbsession_for_unittest,
            post={
                "description": "New Title",
                "amount": 123.00,
            },
        )
        return post_request

    def test_post_updates_information(
        self,
        dbsession_for_unittest,
        example_transactions,
        update_post_request,
    ):
        request = update_post_request
        request.matchdict["transaction_id"] = 1

        from heath.views.transactions import TransactionView
        from pyramid.httpexceptions import HTTPFound

        response = TransactionView(request).update()
        assert isinstance(response, HTTPFound)

        # Check persistence in database
        from heath.models.transaction import Transaction
        first_transaction = dbsession_for_unittest.query(Transaction).first()
        assert first_transaction.id == 1
        assert first_transaction.description == "New Title"
        assert first_transaction.amount == 123.00

    def test_post_update_non_existing_id(
        self,
        dbsession_for_unittest,
        update_post_request,
    ):
        """Test for post to not existing id."""
        request = update_post_request
        request.matchdict["transaction_id"] = 1

        from heath.views.transactions import TransactionView
        from pyramid.httpexceptions import HTTPNotFound
        with pytest.raises(HTTPNotFound):
            TransactionView(request).update()

    def test_invalid_amount(
        self,
        dbsession_for_unittest,
        example_transactions,
        update_post_request,
    ):
        """Test handling when amount is not a number."""
        session = dbsession_for_unittest
        request = update_post_request
        request.POST["amount"] = "Not a number"
        request.matchdict["transaction_id"] = 1

        from heath.views.transactions import TransactionView
        response = TransactionView(request).update()

        # Data is returned into the form
        assert response["errors"][0] == "Amount has to be a number."
        assert response["description"] == "New Title"
        assert response["amount"] == "Not a number"
        # The database content is not updated.
        from heath.models.transaction import Transaction
        first_transaction = session.query(Transaction).first()
        assert first_transaction.description == "First transaction"
        assert first_transaction.amount == 100.00


class TestTransactionDeleteView(object):
    """Unit tests for the transaction delete view."""

    def test_show_only_one_transaction(
        self,
        dummy_request_with_dbsession,
        example_transactions,
    ):
        request = dummy_request_with_dbsession
        request.matchdict["transaction_id"] = 1

        from heath.views.transactions import TransactionView
        response = TransactionView(request).delete()

        assert "transaction" in response
        assert response["transaction"].id == 1
        assert response["transaction"].description == "First transaction"
        assert response["transaction"].amount == 100.00

    def test_404_when_not_existing(
        self,
        dummy_request_with_dbsession,
    ):
        request = dummy_request_with_dbsession
        request.matchdict["transaction_id"] = 3

        from pyramid.httpexceptions import HTTPNotFound
        from heath.views.transactions import TransactionView
        with pytest.raises(HTTPNotFound):
            TransactionView(request).delete()

    # Require deletion confirmation to be set in post.
    # This is just a little extra requirement to prevent posts to the delete
    # endpoints resulting automatically in deletion of the objects
    # Empty posts should not delete an object.
    def test_empty_post_not_deleteting_transaction(
        self,
        dbsession_for_unittest,
        example_transactions,
    ):
        session = dbsession_for_unittest
        request = dummy_request(
            dbsession=session,
            post={},
        )
        request.matchdict["transaction_id"] = 1

        from heath.views.transactions import TransactionView
        from pyramid.httpexceptions import HTTPBadRequest
        with pytest.raises(HTTPBadRequest):
            TransactionView(request).delete()

        # Check that transaction still exists
        from heath.models.transaction import Transaction
        first_transaction = session.query(Transaction).filter_by(id=1).first()
        assert first_transaction == example_transactions[0]

    def test_post_deletes_transaction(
        self,
        dbsession_for_unittest,
        example_transactions,
    ):
        session = dbsession_for_unittest
        request = dummy_request(
            dbsession=session,
            post={"delete.confirm": "delete.confirm"},
        )
        request.matchdict["transaction_id"] = 1

        from heath.views.transactions import TransactionView
        from pyramid.httpexceptions import HTTPFound

        response = TransactionView(request).delete()
        assert isinstance(response, HTTPFound)

        # Check persistence in database
        from heath.models.transaction import Transaction
        first_transaction = session.query(Transaction).filter_by(id=1).first()
        assert first_transaction == None


