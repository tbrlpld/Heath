# -*- coding: utf-8 -*-

"""Unit tests for the transaction views."""

import pytest

from tests.views.conftest import dummy_request


class TestCreateView(object):
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
        with pytest.raises(HTTPFound):
            create(dummy_post_request)

    def test_post_to_create_view(
        self,
        dbsession_for_unittest,
        dummy_post_request,
    ):
        from heath.views.transactions import create
        from pyramid.httpexceptions import HTTPFound
        with pytest.raises(HTTPFound):
            # Usually, a raised exception is treated as test failure.
            # To prevent that, the exception needs to be expected.
            create(dummy_post_request)

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
        with pytest.raises(HTTPFound):
            create(request)
        # Verify creation in database
        from heath.models.transaction import Transaction
        first_transaction = session.query(Transaction).first()
        assert first_transaction.id == 1
        assert first_transaction.description == "New Transaction"
        assert first_transaction.amount == -100.00


class TestListView(object):
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
        example_data_for_unittests,
        dummy_request_with_dbsession,
    ):
        from heath.views.transactions import transactions_list
        return_data = transactions_list(dummy_request_with_dbsession)

        assert "transactions" in return_data
        assert example_data_for_unittests[0] in return_data["transactions"]
        assert example_data_for_unittests[1] in return_data["transactions"]

    def test_transactions_in_reverse_order(
        self,
        example_data_for_unittests,
        dummy_request_with_dbsession,
    ):
        # Test order of transactions (last transaction first in list)
        from heath.views.transactions import transactions_list
        return_data = transactions_list(dummy_request_with_dbsession)

        assert example_data_for_unittests[-1] == return_data["transactions"][0]
        assert example_data_for_unittests[0] == return_data["transactions"][-1]

    def test_transaction_sum(
        self,
        example_data_for_unittests,
        dummy_request_with_dbsession,
    ):
        # Add test for remaining budget returned
        from heath.views.transactions import transactions_list
        return_data = transactions_list(dummy_request_with_dbsession)

        assert return_data["budget"] == 60.0


class TestDetailView(object):
    """Tests for the transaction detail view."""

    def test_show_only_one_transaction(
        self,
        dbsession_for_unittest,
        example_data_for_unittests,
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


class TestEditView(object):
    """Unit tests for the transaction edit view."""

    def test_show_only_one_transaction(
        self,
        dbsession_for_unittest,
        example_data_for_unittests,
    ):
        request = dummy_request(dbsession_for_unittest)
        request.matchdict["transaction_id"] = 1

        from heath.views.transactions import edit
        return_data = edit(request)

        assert "transaction" in return_data
        assert return_data["transaction"].id == 1
        assert return_data["transaction"].description == "First transaction"
        assert return_data["transaction"].amount == 100.00

    def test_404_when_not_existing(self, dbsession_for_unittest):
        request = dummy_request(dbsession_for_unittest)
        request.matchdict["transaction_id"] = 1

        from pyramid.httpexceptions import HTTPNotFound
        from heath.views.transactions import edit
        with pytest.raises(HTTPNotFound):
            edit(request)

    def test_post_updates_information(
        self,
        dbsession_for_unittest,
        example_data_for_unittests,
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

        from heath.views.transactions import edit
        from pyramid.httpexceptions import HTTPFound
        with pytest.raises(HTTPFound):
            edit(request)
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

        from heath.views.transactions import edit
        from pyramid.httpexceptions import HTTPNotFound
        with pytest.raises(HTTPNotFound):
            edit(request)


class TestDeleteView(object):
    """Unit tests for the transaction delete view."""

    def test_show_only_one_transaction(
        self,
        dbsession_for_unittest,
        example_data_for_unittests,
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

    # TODO: Require deletion confirmation to be set in post.
    # This is just a little extra requirement to prevent posts to the delete
    # endpoints resulting automatically in deletion of the objects
    # Empty posts should not delete an object.
    def test_empty_post_not_deleteting_transaction(
        self,
        dbsession_for_unittest,
        example_data_for_unittests,
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
        assert first_transaction == example_data_for_unittests[0]

    def test_post_deletes_transaction(
        self,
        dbsession_for_unittest,
        example_data_for_unittests,
    ):
        session = dbsession_for_unittest
        request = dummy_request(
            dbsession=session,
            post={"delete.confirm": "delete.confirm"},
        )
        request.matchdict["transaction_id"] = 1

        from heath.views.transactions import delete
        from pyramid.httpexceptions import HTTPFound
        with pytest.raises(HTTPFound):
            delete(request)
        # Check persistence in database
        from heath.models.transaction import Transaction
        first_transaction = session.query(Transaction).filter_by(id=1).first()
        assert first_transaction == None


