# -*- coding: utf-8 -*-

"""Tests for the transaction views."""

from ..base import BaseTest, dummy_request, FunctionalBaseTest


class TestCreateTransactionView(BaseTest):
    def test_create_view(self):
        from heath.views.transactions import create

        response = create(dummy_request(self.session))
        self.assertEqual(response, {})


class TestFunctionalCreateTransactionView(FunctionalBaseTest):
    def test_create_view(self):
        resp = self.testapp.get("/create")
        self.assertEqual(resp.status_code, 200)
