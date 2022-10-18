# -*- coding: utf-8 -*-
"""
Created on Mar 13, 2012

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
"""


import logging

from handlers.BaseHandlers import BaseHandler


class NotFoundHandler(BaseHandler):
    def get(self, *args, **kwargs):
        """Renders the 404 page"""
        self.render("public/404.html")

    def post(self, *args, **kwargs):
        """Renders the 404 page"""
        self.render("public/404.html")

    def put(self, *args, **kwargs):
        """Log odd behavior, this should never get legitimately called"""
        logging.warning("%s attempted to use PUT method" % self.request.remote_ip)
        self.render("public/404.html")

    def delete(self, *args, **kwargs):
        """Log odd behavior, this should never get legitimately called"""
        logging.warning("%s attempted to use DELETE method" % self.request.remote_ip)
        self.render("public/404.html")

    def head(self, *args, **kwargs):
        """Log odd behavior, this should never get legitimately called"""
        logging.warning("%s attempted to use HEAD method" % self.request.remote_ip)
        self.render("public/404.html")

    def options(self, *args, **kwargs):
        """Log odd behavior, this should never get legitimately called"""
        logging.warning("%s attempted to use OPTIONS method" % self.request.remote_ip)
        self.render("public/404.html")


class UnauthorizedHandler(BaseHandler):
    def get(self, *args, **kwargs):
        """Renders the 403 page"""
        self.clear_content_policy("object")
        self.add_content_policy("object", "'self'")
        try:
            locked = bool(self.get_argument("locked", "").lower() == "true")
        except ValueError:
            self.render("public/404.html")
            return
        self.render("public/403.html", locked=locked, xsrf=False)


class StopHandler(BaseHandler):
    def get(self, *args, **kwargs):
        """Renders the Game Stopped page"""
        self.render(
            "public/stopped.html", errors=None, info=["The game is currently stopped."]
        )


class NoobHandler(BaseHandler):
    def get(self, *args, **kwargs):
        """Renders the noob page"""
        if self.session is not None:
            user = self.get_current_user()
            logging.info(
                "[NOOB ALERT] %s made a silly request, please mock him (%s)"
                % (user.handle, self.request.remote_ip)
            )
        self.render("public/noob.html")
