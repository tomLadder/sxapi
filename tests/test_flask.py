#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import time
import mock

from flask import Flask

from sxapi.ext import FlaskSX


class TestConfig(object):
    SMAXTEC_API_PRIVATE_ENDPOINT = "http://0.0.0.0:8787/internapi/v0"



class FlaskTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.sxapi = FlaskSX()
        self.sxapi.init_app(self.app)
        self.app.config.from_object(TestConfig)
        self._ctx = self.app.test_request_context()
        self._ctx.push()

    def tearDown(self):
        self._ctx.pop()
        del self.app

    @classmethod
    def setUpClass(cls):
        pass

    def test_init_old(self):
        sxapi = FlaskSX(self.app)

    def test_highlevel_calls(self):
        with self.assertRaises(AttributeError):
            self.sxapi.hello()

        with mock.patch('sxapi.low.BaseAPI.session') as patched_session:
            u = self.sxapi.user
            call = patched_session.get.call_args_list
            self.assertEqual(call[0][0][0], "https://api.smaxtec.com/api/v1/user")

        with mock.patch('sxapi.low.BaseAPI.session') as patched_session:
            u = self.sxapi.get_animal_object("abcd").data
            call = patched_session.get.call_args_list
            self.assertEqual(call[0][0][0], "https://api.smaxtec.com/api/v1/animal/by_id")
            self.assertEqual(call[0][1]["params"]["animal_id"], "abcd")

        with mock.patch('sxapi.low.BaseAPI.session') as patched_session:
            u = self.sxapi.get_organisation_object("abcd").data
            call = patched_session.get.call_args_list
            self.assertEqual(call[0][0][0], "https://api.smaxtec.com/api/v1/organisation/by_id")
            self.assertEqual(call[0][1]["params"]["organisation_id"], "abcd")

    def test_lowlevel_calls(self):
        with mock.patch('sxapi.low.BaseAPI.session') as patched_session:
            u = self.sxapi.get_animal_by_id("abcd")
            call = patched_session.get.call_args_list
            self.assertEqual(call[0][0][0], "https://api.smaxtec.com/api/v1/animal/by_id")
            self.assertEqual(call[0][1]["params"]["animal_id"], "abcd")