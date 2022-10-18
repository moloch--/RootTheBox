# -*- coding: utf-8 -*-
"""
Created on Mar 12, 2012

@author: moloch

    Copyright 2012 Root the Box

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
------------------------------------------------------------------------------

Wrapper for AsyncHTTPTestCase that removed some of the boilerplate code

"""

import logging

try:
    from urllib.parse import quote_plus
except ImportError:
    from urllib import quote_plus
from handlers import app
from tornado.httpclient import HTTPRequest
from tornado.testing import AsyncHTTPTestCase
from libs.StringCoding import decode


class ApplicationTest(AsyncHTTPTestCase):
    """
    Modification of a wrapper class by marxus85
    """

    username = ""
    password = ""
    headers = {}
    cookies = []

    def get_app(self):
        return app

    def get(self, path, authenticated=False, **kwargs):
        if authenticated:
            self._login(self.username, self.password)
        return self._fetch(path, method="GET", **kwargs)

    def post(self, path, authenticated=False, **kwargs):
        """Automatically adds the _xsrf tokens"""
        if authenticated:
            self._login(self.username, self.password)
        if "data" not in kwargs:
            kwargs["data"] = {}
        kwargs["data"]["_xsrf"] = "3858f62230ac3c915f300c664312c63f"
        self.cookies.append("_xsrf=3858f62230ac3c915f300c664312c63f")
        return self._fetch(path, method="POST", **kwargs)

    def _login(self, username, password):
        """Login to the web app and obtain a session_id cookie"""
        try:
            form = {"username": username, "password": password}
            self.post("/login", data=form, follow_redirects=False)
            auth_cookie = "%s;" % self.wait()[0].headers["Set-Cookie"].split(";")[0]
            self.cookies.append("session_id=%s" % auth_cookie)
        except:
            logging.exception("Login failed")

    def _fetch(self, path, **kwargs):
        """Little wrapper to make .fetch easier"""
        data = kwargs.get("data", "")
        if data:
            kwargs.pop("data")
            data = self._form_encode(data)
        method = kwargs["method"]
        if method.upper() == "GET":
            path = "%s?%s" % (path, data)
        elif method.upper() == "POST":
            kwargs["body"] = data
        response = self.fetch(self.get_url(path), headers=self.get_headers(), **kwargs)
        return response, response.body

    def get_headers(self):
        _headers = self.headers
        _headers["Cookie"] = ";".join(self.cookies)
        return _headers

    def _form_encode(self, data):
        """URLEncode parameters"""
        _data = []
        for name, param in list(data.items()):
            _data.append("%s=%s" % (quote_plus(name), quote_plus(param)))
        return "&".join(_data)
