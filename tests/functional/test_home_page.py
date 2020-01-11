# -*- coding: utf-8 -*-

"""Functional tests for the landing page."""

import re

from bs4 import BeautifulSoup
import pytest

from tests.functional.conftest import HTML_PARSER


EXAMPLE_ACCOUNT_NAME = "An Account Name"


@pytest.fixture
def example_account(testapp):
    testapp.post(
        "/accounts/create",
        {
            "name": EXAMPLE_ACCOUNT_NAME,
        },
        status=302,
    )


class TestHomePage(object):
    def test_get_home_status_ok(self, testapp):
        testapp.get("/home", status=200)

    def test_show_message_if_no_accounts(self, testapp):
        response = testapp.get("/home", status=200)

        soup = BeautifulSoup(response.text, HTML_PARSER)
        message_element = soup.find(string="You don't have any accounts yet.")
        assert message_element is not None

    def test_link_to_add_acount_if_no_accounts(self, testapp):
        response = testapp.get("/home", status=200)

        soup = BeautifulSoup(response.text, HTML_PARSER)
        add_account_link = soup.find("a", href=re.compile("/accounts/create"))
        assert add_account_link is not None
        assert add_account_link.text != ""

    def test_existing_accounts_are_shown_on_home(
        self,
        testapp,
        example_account,
    ):
        response = testapp.get("/home", status=200)

        soup = BeautifulSoup(response.text, HTML_PARSER)
        account_name_element = soup.find(text=EXAMPLE_ACCOUNT_NAME)
        assert account_name_element is not None

