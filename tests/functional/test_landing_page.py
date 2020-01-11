# -*- coding: utf-8 -*-

"""Functional tests for the landing page."""


class TestHome(object):
    def test_get_landing(self, testapp):
        testapp.get("/", status=200)
