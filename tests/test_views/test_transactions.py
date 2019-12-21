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
        self.assertIn("message", return_data)
        self.assertEqual(return_data["message"], "Transaction created")

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
    def test_all_transactions_returned(self):
        self.init_database()
        session = self.session
        first_transaction = Transaction(
            description="First transaction",
            amount="100",
        )
        second_transaction = Transaction(
            description="Second transaction",
            amount="-40",
        )
        session.add(first_transaction)
        session.add(second_transaction)

        from heath.views.transactions import transactions_list
        req = dummy_request(dbsession=self.session)
        return_data = transactions_list(req)

        self.assertIn("transactions", return_data)
        self.assertIn(first_transaction, return_data["transactions"])
        self.assertIn(second_transaction, return_data["transactions"])

    # TODO: Test order of transactions (last transaction first in list)
    # TODO: Add test for remaining budget returned

# Functional:
# TODO: Add test for transaction descriptions in list view
# TODO: Add test for link to detail pages
# TODO: Add test for link to create transaction page
