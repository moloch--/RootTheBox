# -*- coding: utf-8 -*-
"""
Created on Mar 15, 2012

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
----------------------------------------------------------------------------

This file contains the base handlers, all other handlers should inherit
from these base classes.

"""
# pylint: disable=unused-wildcard-import,no-member


import logging
import memcache
import traceback
import datetime, time

from models import dbsession, chatsession
from models.User import User
from libs.SecurityDecorators import *
from libs.Sessions import MemcachedSession
from libs.EventManager import EventManager
from builtins import str

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
from tornado.web import RequestHandler
from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler
from tornado.options import options


class BaseHandler(RequestHandler):

    """ User handlers extend this class """

    csp = {
        "default-src": set(["'self'"]),
        "script-src": set(["'self'"]),
        "connect-src": set(["'self'"]),
        "frame-src": set(["'self'"]),
        "img-src": set(["'self'"]),
        "media-src": set(["'none'"]),
        "font-src": set(["'self'"]),
        "object-src": set(["'none'"]),
        "style-src": set(["'self'"]),
    }
    _session = None
    dbsession = dbsession
    chatsession = chatsession
    _memcached = None
    new_events = []
    io_loop = IOLoop.instance()
    event_manager = EventManager.instance()
    config = options  # backward compatability

    def initialize(self):
        """ Setup sessions, etc """
        self.add_content_policy("connect-src", self.config.origin)
        # We need this for a few things, and so far as I know it doesn't
        # present too much of a security risk - TODO: no longer require
        # inline styles
        self.add_content_policy("style-src", "'unsafe-inline'")

    def get_current_user(self):
        """ Get current user object from database """
        if self.session is not None:
            try:
                return User.by_uuid(self.session["user_uuid"])
            except KeyError:
                logging.exception("Malformed session: %r" % self.session)
            except:
                logging.exception("Failed call to get_current_user()")
        return None

    def start_session(self):
        """ Starts a new session """
        self.session = self._create_session()
        flags = {"expires": self.session.expires, "path": "/", "HttpOnly": True}
        if self.config.ssl:
            flags["Secure"] = True
        self.set_secure_cookie("session_id", self.session.session_id, **flags)

    def add_content_policy(self, src, policy):
        """ Add to the existing CSP header """
        if not src.endswith("-src"):
            src += "-src"
        if src in self.csp:
            self.csp[src].add(policy)
            self._refresh_csp()
        else:
            raise ValueError("Invalid content source")

    def clear_content_policy(self, src):
        """ Clear a content source in the existing CSP header """
        if not src.endswith("-src"):
            src += "-src"
        if src in self.csp:
            self.csp[src] = set()
            self._refresh_csp()
        else:
            raise ValueError("Invalid content source")

    def _refresh_csp(self):
        """ Rebuild the Content-Security-Policy header """
        _csp = []
        for src, policies in list(self.csp.items()):
            if len(policies):
                _csp.append("%s %s; " % (src, " ".join(policies)))
        csp = "".join(_csp)
        # Disabled until i can figure out the bug
        # self.set_header("Content-Security-Policy", csp)

    @property
    def memcached(self):
        """ Connects to Memcached instance """
        if self._memcached is None:
            self._memcached = memcache.Client([self.config.memcached], debug=0)
        return self._memcached

    def _create_session(self):
        """ Creates a new session """
        kwargs = {"connection": self.memcached, "ip_address": self.request.remote_ip}
        new_session = MemcachedSession(**kwargs)
        new_session.save()
        return new_session

    def flush_memcached(self):
        if self._memcached is not None:
            self._memcached.flush_all()

    @property
    def session(self):
        if self._session is None:
            session_id = self.get_secure_cookie("session_id")
            if session_id is not None:
                self._session = self._get_session(session_id)
        return self._session

    @session.setter
    def session(self, new_session):
        self._session = new_session

    def _get_session(self, session_id):
        kwargs = {
            "connection": self.memcached,
            "session_id": session_id,
            "ip_address": self.request.remote_ip,
        }
        old_session = MemcachedSession.load(**kwargs)
        if old_session and not old_session.is_expired():
            old_session.refresh()
            return old_session
        else:
            return None

    def set_default_headers(self):
        """
        Set security HTTP headers, and add some troll-y version headers
        """
        self.set_header("Server", "Microsoft-IIS/7.5")
        self.add_header("X-Powered-By", "ASP.NET")
        self.add_header("X-Frame-Options", "DENY")
        self.add_header("X-XSS-Protection", "1; mode=block")
        self.add_header("X-Content-Type-Options", "nosniff")
        self._refresh_csp()
        if self.config.ssl:
            self.add_header(
                "Strict-Transport-Security", "max-age=31536000; includeSubDomains;"
            )

    def write_error(self, status_code, **kwargs):
        """ Write our custom error pages """
        trace = "".join(traceback.format_exception(*kwargs["exc_info"]))
        logging.error(
            "Request from %s resulted in an error code %d:\n%s"
            % (self.request.remote_ip, status_code, trace)
        )
        if status_code in [403]:
            # This should only get called when the _xsrf check fails,
            # all other '403' cases we just send a redirect to /403
            # self.render('public/403.html', locked=False, xsrf=True)
            self.redirect("/logout")  # just log them out
        else:
            if not self.config.debug:
                # Never tell the user we got a 500
                self.render("public/404.html")
            else:
                # If debug mode is enabled, just call Tornado's write_error()
                super(BaseHandler, self).write_error(status_code, **kwargs)

    def get(self, *args, **kwargs):
        """ Placeholder, incase child class does not impl this method """
        self.render("public/404.html")

    def post(self, *args, **kwargs):
        """ Placeholder, incase child class does not impl this method """
        self.render("public/404.html")

    def put(self, *args, **kwargs):
        """ Log odd behavior, this should never get legitimately called """
        logging.warn("%s attempted to use PUT method" % self.request.remote_ip)

    def delete(self, *args, **kwargs):
        """ Log odd behavior, this should never get legitimately called """
        logging.warn("%s attempted to use DELETE method" % self.request.remote_ip)

    def head(self, *args, **kwargs):
        """ Ignore it """
        logging.warn("%s attempted to use HEAD method" % self.request.remote_ip)

    def options(self, *args, **kwargs):
        """ Log odd behavior, this should never get legitimately called """
        logging.warn("%s attempted to use OPTIONS method" % self.request.remote_ip)

    def on_finish(self, *args, **kwargs):
        """ Called after a response is sent to the client """
        self.dbsession.close()

    def timer(self):
        timer = None
        if self.application.settings["freeze_scoreboard"]:
            timerdiff = self.application.settings["freeze_scoreboard"] - time.time()
            if timerdiff < 0:
                timerdiff = 0
            timer = str(timerdiff)
        return timer


class BaseWebSocketHandler(WebSocketHandler):

    """ Handles websocket connections """

    _session = None
    _memcached = None
    io_loop = IOLoop.instance()
    manager = EventManager.instance()
    config = options  # backward compatability

    def check_origin(self, origin):
        """ Parses the request's origin header """
        try:
            request_origin = urlparse(origin)
            origin = urlparse(self.config.origin)
            logging.debug(
                "Checking request origin '%s' ends with '%s'" % (request_origin, origin)
            )
            return request_origin.netloc.endswith(origin)
        except:
            logging.exception("Failed to parse request origin: %r" % origin)
            return False

    @property
    def memcached(self):
        """ Connects to Memcached instance """
        if self._memcached is None:
            self._memcached = memcache.Client([self.config.memcached], debug=0)
        return self._memcached

    @property
    def session(self):
        if self._session is None:
            session_id = self.get_secure_cookie("session_id")
            if session_id is not None:
                self._session = self._get_session(session_id)
        return self._session

    @session.setter
    def session(self, new_session):
        self._session = new_session

    def _get_session(self, session_id):
        kwargs = {
            "connection": self.memcached,
            "session_id": session_id,
            "ip_address": self.request.remote_ip,
        }
        old_session = MemcachedSession.load(**kwargs)
        if old_session and not old_session.is_expired():
            old_session.refresh()
            return old_session
        else:
            return None

    def get_current_user(self):
        """ Get current user object from database """
        if self.session is not None:
            try:
                return User.by_handle(self.session["handle"])
            except KeyError:
                logging.exception("Malformed session: %r" % self.session)
            except:
                logging.exception("Failed call to get_current_user()")
        return None

    def open(self):
        pass

    def on_message(self, message):
        pass

    def on_close(self):
        pass
