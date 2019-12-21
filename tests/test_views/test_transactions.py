# -*- coding: utf-8 -*-

"""Tests for the transaction views."""

from heath.models.transaction import Transaction

from ..base import BaseTest, dummy_request, FunctionalBaseTest


class TestCreateTransactionViewFunction(BaseTest):
    def test_create_view(self):
        from heath.views.transactions import create

        return_data = create(dummy_request(self.session))
        self.assertEqual(return_data, {})

    def test_post_to_create_view(self):
        self.init_database()

        from heath.views.transactions import create

        req = dummy_request(
            dbsession=self.session,
            post={
                "description": "New Transaction",
                "amount": "100",
            },
        )
        return_data = create(req)

        first_transaction = req.dbsession.query(Transaction).first()
        self.assertEqual(first_transaction.id, 1)
        self.assertEqual(first_transaction.description, "New Transaction")
        self.assertEqual(first_transaction.amount, 100)

    # TODO: Add test for negative amount


class FunctionalTestCreateTransactionView(FunctionalBaseTest):
    def test_form_in_create_view(self):
        resp = self.testapp.get("/create")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Create Transaction", resp.body)
        self.assertIn(b"<form", resp.body)
        self.assertIn(b'name="description"', resp.body)
        self.assertIn(b'name="amount"', resp.body)
        self.assertIn(b'step="0.01"', resp.body)


class TestTransactionsListView(BaseTest):
    def setUp(self):
        super().setUp()
        self.init_database()
        session = self.session
        self.first_transaction = Transaction(
            description="First transaction",
            amount="100",
        )
        self.second_transaction = Transaction(
            description="Second transaction",
            amount="-40",
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
            60,
        )

# Functional:
# class FunctionaltTestTransactionsListView(FunctionalBaseTest):
# TODO: Add test for transaction descriptions in list view.
#       For some reason, the database does not initialize when an app
#       object is created. This causes tests for views that rely on data from
#       the database to fail with ""no such tables" error.
#     def test_list_url(self):
#         resp = self.testapp.get("/list")
#         self.assertEqual(resp.status_code, 200)
# TODO: Add test for link to detail pages
# TODO: Add test for link to create transaction page

class TestTransactionDetailView(BaseTest):
    def setUp(self):
        super().setUp()
        self.init_database()
        session = self.session
        self.first_transaction = Transaction(
            description="First transaction",
            amount="100",
        )
        self.second_transaction = Transaction(
            description="Second transaction",
            amount="-40",
        )
        session.add(self.first_transaction)
        session.add(self.second_transaction)

    def test_show_only_one_transaction(self):
        request = dummy_request(self.session)
        request.matchdict["transaction_id"] = 1

        from heath.views.transactions import detail
        return_data = detail(request)

        self.assertIn("transaction", return_data)
        self.assertEqual(return_data["transaction"].id, 1)
        self.assertEqual(
            return_data["transaction"].description, "First transaction"
        )
        self.assertEqual(return_data["transaction"].amount, "100")

    def test_404_when_not_existing(self):
        request = dummy_request(self.session)
        request.matchdict["transaction_id"] = 3

        from heath.views.transactions import detail
        return_data = detail(request)

        self.assertEqual(return_data.code, 404)

