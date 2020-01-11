# -*- coding: utf-8 -*-

"""Functional tests for the landing page."""


class TestLandingPage(object):
    def test_get_landing_status_ok(self, testapp):
        testapp.get("/", status=200)
