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


class TestTransactionCreateView(object):
    """Test for the create view."""

    def test_create_view(self, dbsession_for_unittest):
        from heath.views.transactions import create
        return_data = create(dummy_request(dbsession_for_unittest))
        assert return_data == {}

    @pytest.fixture
    def dummy_post_request(self, dbsession_for_unittest):
        return dummy_request(
            dbsession=dbsession_for_unittest,
            post={
                "description": "New Transaction",
                "amount": 100.00,
            },
        )

    def test_redirect_after_successful_creation(self, dummy_post_request):
        from heath.views.transactions import create
        from pyramid.httpexceptions import HTTPFound

        response = create(dummy_post_request)
        assert isinstance(response, HTTPFound)

    def test_post_to_create_view(
        self,
        dbsession_for_unittest,
        dummy_post_request,
    ):
        from heath.views.transactions import create
        from pyramid.httpexceptions import HTTPFound

        response = create(dummy_post_request)
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
        from heath.views.transactions import create
        from pyramid.httpexceptions import HTTPFound

        response = create(request)
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

        from heath.views.transactions import create
        response = create(request)
        assert response["errors"][0] == "Amount has to be a number."
        assert response["description"] == "New Transaction"
        assert response["amount"] == "Not a number"

        # Verify no creation in database
        from heath.models.transaction import Transaction
        first_transaction = session.query(Transaction).first()
        assert first_transaction is None


class TestTransactionListView(object):
    """Unit tests for transaction list view."""

    @pytest.fixture
    def dummy_request_with_dbsession(self, dbsession_for_unittest):
        return dummy_request(dbsession=dbsession_for_unittest)

    def test_zero_budget(self, dummy_request_with_dbsession):
        """Return zero buget when no transactions exist."""
        from heath.views.transactions import transactions_list
        response = transactions_list(dummy_request_with_dbsession)

        assert response["budget"] == 0.0

    def test_empty_transactios_list(self, dummy_request_with_dbsession):
        """Return empty transactions list."""
        from heath.views.transactions import transactions_list
        response = transactions_list(dummy_request_with_dbsession)

        assert response["transactions"] == []

    def test_all_transactions_returned(
        self,
        example_transactions,
        dummy_request_with_dbsession,
    ):
        from heath.views.transactions import transactions_list
        return_data = transactions_list(dummy_request_with_dbsession)

        assert "transactions" in return_data
        assert example_transactions[0] in return_data["transactions"]
        assert example_transactions[1] in return_data["transactions"]

    def test_transactions_in_reverse_order(
        self,
        example_transactions,
        dummy_request_with_dbsession,
    ):
        # Test order of transactions (last transaction first in list)
        from heath.views.transactions import transactions_list
        return_data = transactions_list(dummy_request_with_dbsession)

        assert example_transactions[-1] == return_data["transactions"][0]
        assert example_transactions[0] == return_data["transactions"][-1]

    def test_transaction_sum(
        self,
        example_transactions,
        dummy_request_with_dbsession,
    ):
        # Add test for remaining budget returned
        from heath.views.transactions import transactions_list
        return_data = transactions_list(dummy_request_with_dbsession)

        assert return_data["budget"] == 60.0


class TestTransactionDetailView(object):
    """Tests for the transaction detail view."""

    def test_show_only_one_transaction(
        self,
        dbsession_for_unittest,
        example_transactions,
    ):
        request = dummy_request(dbsession_for_unittest)
        request.matchdict["transaction_id"] = 1

        from heath.views.transactions import detail
        return_data = detail(request)

        assert "transaction" in return_data
        assert return_data["transaction"].id == 1
        assert return_data["transaction"].description == "First transaction"
        assert return_data["transaction"].amount == 100.00

    def test_404_when_not_existing(
        self,
        dbsession_for_unittest,
    ):
        request = dummy_request(dbsession_for_unittest)
        request.matchdict["transaction_id"] = 1

        from pyramid.httpexceptions import HTTPNotFound
        from heath.views.transactions import detail
        with pytest.raises(HTTPNotFound):
            detail(request)


class TestTransactionUpdateView(object):
    """Unit tests for the transaction edit view."""

    def test_show_only_one_transaction(
        self,
        dbsession_for_unittest,
        example_transactions,
    ):
        request = dummy_request(dbsession_for_unittest)
        request.matchdict["transaction_id"] = 1

        from heath.views.transactions import update
        return_data = update(request)

        assert "transaction" in return_data
        assert return_data["transaction"].id == 1
        assert return_data["transaction"].description == "First transaction"
        assert return_data["transaction"].amount == 100.00

    def test_404_when_not_existing(self, dbsession_for_unittest):
        request = dummy_request(dbsession_for_unittest)
        request.matchdict["transaction_id"] = 1

        from pyramid.httpexceptions import HTTPNotFound
        from heath.views.transactions import update
        with pytest.raises(HTTPNotFound):
            update(request)

    def test_post_updates_information(
        self,
        dbsession_for_unittest,
        example_transactions,
    ):
        session = dbsession_for_unittest
        request = dummy_request(
            dbsession=session,
            post={
                "description": "The First Transaction",
                "amount": 123.00,
            },
        )
        request.matchdict["transaction_id"] = 1

        from heath.views.transactions import update
        from pyramid.httpexceptions import HTTPFound

        response = update(request)
        assert isinstance(response, HTTPFound)

        # Check persistence in database
        from heath.models.transaction import Transaction
        first_transaction = session.query(Transaction).first()
        assert first_transaction.id == 1
        assert first_transaction.description == "The First Transaction"
        assert first_transaction.amount == 123.00

    def test_post_update_non_existing_id(
        self,
        dbsession_for_unittest,
    ):
        """Test for post to not existing id."""
        session = dbsession_for_unittest
        request = dummy_request(
            dbsession=session,
            post={
                "description": "The First Transaction",
                "amount": 123.00,
            },
        )
        request.matchdict["transaction_id"] = 1

        from heath.views.transactions import update
        from pyramid.httpexceptions import HTTPNotFound
        with pytest.raises(HTTPNotFound):
            update(request)

    def test_invalid_amount(self, dbsession_for_unittest, example_transactions):
        """Test handling when amount is not a number."""
        session = dbsession_for_unittest
        request = dummy_request(
            dbsession=session,
            post={
                "description": "New Title",
                "amount": "Not a number",
            },
        )
        request.matchdict["transaction_id"] = 1

        from heath.views.transactions import update
        response = update(request)

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
        dbsession_for_unittest,
        example_transactions,
    ):
        request = dummy_request(dbsession_for_unittest)
        request.matchdict["transaction_id"] = 1

        from heath.views.transactions import delete
        return_data = delete(request)

        assert "transaction" in return_data
        assert return_data["transaction"].id == 1
        assert return_data["transaction"].description == "First transaction"
        assert return_data["transaction"].amount == 100.00

    def test_404_when_not_existing(
        self,
        dbsession_for_unittest,
    ):
        request = dummy_request(dbsession_for_unittest)
        request.matchdict["transaction_id"] = 3

        from pyramid.httpexceptions import HTTPNotFound
        from heath.views.transactions import delete
        with pytest.raises(HTTPNotFound):
            delete(request)

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

        from heath.views.transactions import delete
        from pyramid.httpexceptions import HTTPBadRequest
        with pytest.raises(HTTPBadRequest):
            delete(request)
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

        from heath.views.transactions import delete
        from pyramid.httpexceptions import HTTPFound

        response = delete(request)
        assert isinstance(response, HTTPFound)

        # Check persistence in database
        from heath.models.transaction import Transaction
        first_transaction = session.query(Transaction).filter_by(id=1).first()
        assert first_transaction == None


