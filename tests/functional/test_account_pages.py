# -*- coding: utf-8 -*-

"""Functional tests for the landing page."""

from bs4 import BeautifulSoup
import re

from tests.functional.conftest import HTML_PARSER


class TestAccountAddPage(object):
    def test_get_account_add_status_ok(self, testapp):
        testapp.get("/accounts/add", status=200)

    def test_form_in_add_acount_page(self, testapp):
        response = testapp.get("/accounts/add", status=200)

        soup = BeautifulSoup(response.text, HTML_PARSER)
        form_element = soup.find("form")
        assert form_element is not None

    def test_submitting_form_leads_to_redirect(self, testapp):
        get_response = testapp.get("/accounts/add", status=200)
        form = get_response.form
        form["name"] = "An Account Name"

        # Submit the form
        submit_response = form.submit("create")

        assert submit_response.status_code == 302

    def test_submitting_form_redirects_to_page_that_shows_account(
        self,
        testapp,
    ):
        get_response = testapp.get("/accounts/add", status=200)
        form = get_response.form
        form["name"] = "An Account Name"

        # Submit the form and follow redirect
        submit_response = form.submit("create")
        follow_response = submit_response.follow()

        soup = BeautifulSoup(follow_response.text, HTML_PARSER)
        account_name_element = soup.find(text="An Account Name")
        assert account_name_element is not None

    def test_correct_post_leads_to_redirect(self, testapp):
        testapp.post(
            "/accounts/add",
            {
                "name": "An Account Name",
            },
            status=302,
        )

    def test_cancel_link_exists_on_create_page(self, testapp):
        response = testapp.get("/accounts/add", status=200)

        soup = BeautifulSoup(response.text, HTML_PARSER)
        cancel_link = soup.find("a", text="Cancel")
        assert cancel_link is not None

    def test_cancel_links_to_home_if_visited_directy(self, testapp):
        response = testapp.get("/accounts/add", status=200)

        soup = BeautifulSoup(response.text, HTML_PARSER)
        cancel_link = soup.find("a", text="Cancel")
        assert cancel_link is not None
        assert "/home" in cancel_link["href"]

    # TODO: Cancel link goes to previous page (referrer) if visited from
    #       somewhere and not directly.

