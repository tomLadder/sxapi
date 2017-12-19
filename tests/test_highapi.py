#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import time
import mock

from sxapi import API


class HighApiTests(unittest.TestCase):
    PUBLIC_ENDPOINT = "http://0.0.0.0:8989/publicapi/v1"
    EMAIL = "myuser@smaxtec.com"
    PASSWORD = "mypassword"

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @classmethod
    def setUpClass(cls):
        pass

    def test_status(self):
        api = API(email=self.EMAIL, password=self.PASSWORD, endpoint=self.PUBLIC_ENDPOINT)
        with mock.patch('sxapi.low.BaseAPI.session') as patched_session:
            r = api.status
            call = patched_session.get.call_args_list
            self.assertEqual(call[0][0][0], "http://0.0.0.0:8989/publicapi/v1/service/status")
