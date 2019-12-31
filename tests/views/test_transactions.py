# -*- coding: utf-8 -*-

"""Tests for the transaction views."""

import transaction

from heath.models.transaction import Transaction

from tests.base import BaseTest, dummy_request


class TestCreateTransactionViewFunction(BaseTest):
    def test_create_view(self):
        from heath.views.transactions import create
        return_data = create(dummy_request(self.session))
        self.assertEqual(return_data, {})

    def test_redirect_after_successful_creation(self):
        request = dummy_request(
            dbsession=self.session,
            post={
                "description": "New Transaction",
                "amount": 100.00,
            },
        )

        from heath.views.transactions import create
        from pyramid.httpexceptions import HTTPFound
        with self.assertRaises(HTTPFound):
            create(request)

    def test_post_to_create_view(self):
        request = dummy_request(
            dbsession=self.session,
            post={
                "description": "New Transaction",
                "amount": 100.00,
            },
        )
        from heath.views.transactions import create
        from pyramid.httpexceptions import HTTPFound
        with self.assertRaises(HTTPFound):
            # Usually, a raised exception is treated as test failure.
            # To prevent that, the exception needs to be expected.
            create(request)
        # Verify creation in database
        first_transaction = self.session.query(Transaction).first()
        self.assertEqual(first_transaction.id, 1)
        self.assertEqual(first_transaction.description, "New Transaction")
        self.assertEqual(first_transaction.amount, 100.00)

    def test_negative_amount(self):
        request = dummy_request(
            dbsession=self.session,
            post={
                "description": "New Transaction",
                "amount": -100.00,
            },
        )
        from heath.views.transactions import create
        from pyramid.httpexceptions import HTTPFound
        with self.assertRaises(HTTPFound):
            create(request)
        # Verify creation in database
        first_transaction = self.session.query(Transaction).first()
        self.assertEqual(first_transaction.id, 1)
        self.assertEqual(first_transaction.description, "New Transaction")
        self.assertEqual(first_transaction.amount, -100.00)


class TestTransactionsListView(BaseTest):
    def setUp(self):
        super().setUp()

        session = self.session
        self.first_transaction = Transaction(
            description="First transaction",
            amount=100.00,
        )
        self.second_transaction = Transaction(
            description="Second transaction",
            amount=-40.00,
        )
        session.add(self.first_transaction)
        session.add(self.second_transaction)

    def test_all_transactions_returned(self):
        from heath.views.transactions import transactions_list
        req = dummy_request(dbsession=self.session)
        return_data = transactions_list(req)

        self.assertIn("transactions", return_data)
        self.assertIn(self.first_transaction, return_data["transactions"])
        self.assertIn(self.second_transaction, return_data["transactions"])

    def test_transactions_in_reverse_order(self):
        # Test order of transactions (last transaction first in list)
        from heath.views.transactions import transactions_list
        req = dummy_request(dbsession=self.session)
        return_data = transactions_list(req)

        self.assertEqual(
            self.second_transaction,
            return_data["transactions"][0],
        )
        self.assertEqual(
            self.first_transaction,
            return_data["transactions"][1],
        )

    def test_transaction_sum(self):
        # Add test for remaining budget returned
        from heath.views.transactions import transactions_list
        req = dummy_request(dbsession=self.session)
        return_data = transactions_list(req)

        self.assertEqual(
            return_data["budget"],
            60.0,
        )


class TestTransactionsListViewNoTransactions(BaseTest):
    def setUp(self):
        super().setUp()

    def test_zero_budget(self):
        """Return zero buget when no transactions exist."""
        from heath.views.transactions import transactions_list
        request = dummy_request(dbsession=self.session)
        response = transactions_list(request)

        self.assertEqual(response["budget"], 0.0)

    def test_empty_transactios_list(self):
        """Return empty transactions list."""
        from heath.views.transactions import transactions_list
        request = dummy_request(dbsession=self.session)
        response = transactions_list(request)

        self.assertEqual(response["transactions"], [])


class TestTransactionDetailView(BaseTest):
    def setUp(self):
        super().setUp()
        session = self.session
        self.first_transaction = Transaction(
            description="First transaction",
            amount=100.00,
        )
        session.add(self.first_transaction)

    def test_show_only_one_transaction(self):
        request = dummy_request(self.session)
        request.matchdict["transaction_id"] = 1

        from heath.views.transactions import detail
        return_data = detail(request)

        self.assertIn("transaction", return_data)
        self.assertEqual(return_data["transaction"].id, 1)
        self.assertEqual(
            return_data["transaction"].description, "First transaction",
        )
        self.assertEqual(return_data["transaction"].amount, 100.00)

    def test_404_when_not_existing(self):
        request = dummy_request(self.session)
        request.matchdict["transaction_id"] = 3

        from pyramid.httpexceptions import HTTPNotFound
        from heath.views.transactions import detail
        with self.assertRaises(HTTPNotFound):
            detail(request)


class TestTransactionEditView(BaseTest):
    def setUp(self):
        super().setUp()
        session = self.session
        self.first_transaction = Transaction(
            description="First transaction",
            amount=100.00,
        )
        session.add(self.first_transaction)

    def test_show_only_one_transaction(self):
        request = dummy_request(self.session)
        request.matchdict["transaction_id"] = 1

        from heath.views.transactions import edit
        return_data = edit(request)

        self.assertIn("transaction", return_data)
        self.assertEqual(return_data["transaction"].id, 1)
        self.assertEqual(
            return_data["transaction"].description, "First transaction",
        )
        self.assertEqual(return_data["transaction"].amount, 100.00)

    def test_404_when_not_existing(self):
        request = dummy_request(self.session)
        request.matchdict["transaction_id"] = 3

        from pyramid.httpexceptions import HTTPNotFound
        from heath.views.transactions import edit
        with self.assertRaises(HTTPNotFound):
            edit(request)

    def test_post_updates_information(self):
        request = dummy_request(
            dbsession=self.session,
            post={
                "description": "The First Transaction",
                "amount": 123.00,
            },
        )
        request.matchdict["transaction_id"] = 1

        from heath.views.transactions import edit
        from pyramid.httpexceptions import HTTPFound
        with self.assertRaises(HTTPFound):
            edit(request)
        # Check persistence in database
        first_transaction = self.session.query(Transaction).first()
        self.assertEqual(first_transaction.id, 1)
        self.assertEqual(first_transaction.description, "The First Transaction")
        self.assertEqual(first_transaction.amount, 123.00)


class TestTransactionDeleteView(BaseTest):
    def setUp(self):
        super().setUp()
        session = self.session
        self.first_transaction = Transaction(
            description="First transaction",
            amount=100.00,
        )
        session.add(self.first_transaction)

    def test_show_only_one_transaction(self):
        request = dummy_request(self.session)
        request.matchdict["transaction_id"] = 1

        from heath.views.transactions import delete
        return_data = delete(request)

        self.assertIn("transaction", return_data)
        self.assertEqual(return_data["transaction"].id, 1)
        self.assertEqual(
            return_data["transaction"].description, "First transaction",
        )
        self.assertEqual(return_data["transaction"].amount, 100.00)

    def test_404_when_not_existing(self):
        request = dummy_request(self.session)
        request.matchdict["transaction_id"] = 3

        from pyramid.httpexceptions import HTTPNotFound
        from heath.views.transactions import delete
        with self.assertRaises(HTTPNotFound):
            delete(request)

    def test_post_deletes_transaction(self):
        request = dummy_request(
            dbsession=self.session,
            post={
                "description": "The First Transaction",
                "amount": 123.00,
            },
        )
        request.matchdict["transaction_id"] = 1

        from heath.views.transactions import delete
        from pyramid.httpexceptions import HTTPFound
        with self.assertRaises(HTTPFound):
            delete(request)

        first_transaction = self.session.query(Transaction).first()
        self.assertEqual(first_transaction, None)
