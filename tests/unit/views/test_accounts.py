# -*- coding: utf-8 -*-

"""Unit tests for the transaction views."""

import pytest

from tests.unit.views.conftest import dummy_request


# @pytest.fixture
# def example_transactions(dbsession_for_unittest):
#     session = dbsession_for_unittest
#     from heath.models.transaction import Transaction
#     first_transaction = Transaction(
#         description="First transaction",
#         amount=100.00,
#     )
#     second_transaction = Transaction(
#         description="Second transaction",
#         amount=-40.00,
#     )
#     session.add(first_transaction)
#     session.add(second_transaction)
#     return (
#         first_transaction,
#         second_transaction,
#     )


class TestAccountCreateView(object):
    """Test for the create view."""

    @pytest.fixture
    def dummy_post_create_request(
        self,
        dummy_post_request,
    ):
        """Create dummy post request with payload for new transaction."""
        dummy_post_request.POST = {
            "name": "A New Account",
        }
        return dummy_post_request

    def test_empty_post_leads_to_bad_request(self, dummy_post_request):
        from pyramid.httpexceptions import HTTPBadRequest

        from heath.views.accounts import AccountViews
        with pytest.raises(HTTPBadRequest):
            AccountViews(dummy_post_request).create_post()

    def test_empty_name_leads_to_error_message(
        self,
        dummy_post_create_request,
    ):
        dummy_post_create_request.POST["name"] = ""

        from heath.views.accounts import AccountViews
        response = AccountViews(dummy_post_create_request).create_post()

        assert "Name can not be empty." in response["errors"]

    def test_post_creates_account_in_db(
        self,
        dummy_post_create_request,
        dbsession_for_unittest,
    ):
        from heath.views.accounts import AccountViews
        AccountViews(dummy_post_create_request).create_post()

        # Verify creation in database
        from heath.models.account import Account
        account = dbsession_for_unittest.query(Account).first()
        assert account.id == 1
        assert account.name == "A New Account"

    def test_redirect_after_successful_creation(
        self,
        dummy_post_create_request,
    ):
        from heath.views.accounts import AccountViews
        from pyramid.httpexceptions import HTTPFound

        response = AccountViews(dummy_post_create_request).create_post()
        assert isinstance(response, HTTPFound)


