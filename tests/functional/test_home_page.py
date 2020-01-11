# -*- coding: utf-8 -*-

"""Functional tests for the landing page."""

from bs4 import BeautifulSoup
import re

from tests.functional.conftest import HTML_PARSER


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
        add_account_link = soup.find("a", href=re.compile("/accounts/add"))
        assert add_account_link is not None
