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
        print(first_transaction)
        self.assertEqual(first_transaction.id, 1)
        self.assertEqual(first_transaction.description, "New Transaction")
        self.assertEqual(first_transaction.amount, 100)


class FunctionalTestCreateTransactionView(FunctionalBaseTest):
    def test_form_in_create_view(self):
        resp = self.testapp.get("/create")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Create Transaction", resp.body)
        self.assertIn(b"<form", resp.body)
        self.assertIn(b'name="description"', resp.body)
        self.assertIn(b'name="amount"', resp.body)
        self.assertIn(b'step="0.01"', resp.body)
