# -*- coding: utf-8 -*-

"""Functional tests for the landing page."""


class TestHomePage(object):
    def test_get_home_status_ok(self, testapp):
        testapp.get("/home", status=200)
