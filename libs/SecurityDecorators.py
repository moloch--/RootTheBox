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
import functools

from models.User import User
from tornado.options import options


def authenticated(method):
    """Checks to see if a user has been authenticated"""

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.session is not None:
            if self.session.ip_address == self.request.remote_ip:
                if (
                    self.request.remote_ip
                    not in self.application.settings["blacklisted_ips"]
                ):
                    user = self.get_current_user()
                    if user is None:
                        self.session.delete()
                        self.clear_all_cookies()
                        self.redirect(self.application.settings["login_url"])
                    elif not user.locked:
                        return method(self, *args, **kwargs)
                    else:
                        self.session.delete()
                        self.clear_all_cookies()
                        self.redirect("/403?locked=true")
                else:
                    self.session.delete()
                    self.clear_all_cookies()
                    self.redirect(self.application.settings["login_url"])
            else:
                logging.warning(
                    "Session hijack attempt from %s?" % (self.request.remote_ip,)
                )
                self.session.delete()
                self.clear_all_cookies()
                self.redirect(self.application.settings["login_url"])
        else:
            self.redirect(self.application.settings["login_url"])

    return wrapper


def game_started(method):
    """Checks to see if the game is running"""

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.application.settings["game_started"]:
            user = self.get_current_user()
            if user is None or not user.is_admin():
                self.redirect("/gamestatus")
        return method(self, *args, **kwargs)

    return wrapper


def restrict_ip_address(method):
    """Only allows access to ip addresses in a provided list"""

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if (
            len(self.application.settings["admin_ips"]) == 0
            or self.request.remote_ip in self.application.settings["admin_ips"]
        ):
            return method(self, *args, **kwargs)
        else:
            logging.warning(
                "Attempted unauthorized access from %s to %s"
                % (self.request.remote_ip, self.request.uri)
            )
            self.redirect(self.application.settings["forbidden_url"])

    return wrapper


def blacklist_ips(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.request.remote_ip not in self.application.settings["blacklisted_ips"]:
            return method(self, *args, **kwargs)
        else:
            self.render("public/login.html", errors=None)

    return wrapper


def authorized(permission):
    """Checks user's permissions"""

    def func(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if self.session is not None:
                user = User.by_handle(self.session["handle"])
                if user is not None and user.has_permission(permission):
                    return method(self, *args, **kwargs)
            logging.warning(
                "Attempted unauthorized access from %s to %s"
                % (self.request.remote_ip, self.request.uri)
            )
            self.redirect(self.application.settings["forbidden_url"])

        return wrapper

    return func


def debug(method):
    """Logs a method call/return"""

    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        class_name = args[0].__class__.__name__
        logging.debug("Call to -> %s.%s()" % (class_name, method.__name__))
        value = method(*args, **kwargs)
        logging.debug("Return from <- %s.%s()" % (class_name, method.__name__))
        return value

    return wrapper


def has_item(name):
    """Checks user's team owns an unlock/item"""

    def func(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            user = self.get_current_user()
            if user is not None and user.has_item(name):
                return method(self, *args, **kwargs)
            else:
                logging.warning(
                    "Attempted unauthorized access from %s to %s"
                    % (self.request.remote_ip, self.request.uri)
                )
                self.redirect(self.application.settings["forbidden_url"])

        return wrapper

    return func
    
def item_allowed(name):
    """Checks an unlock/item is allowed to use"""

    def func(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if name in options.allowed_market_items:
                return method(self, *args, **kwargs)
            else:
                logging.warning(
                    "Attempted unauthorized access from %s to %s"
                    % (self.request.remote_ip, self.request.uri)
                )
                self.redirect(self.application.settings["forbidden_url"])

        return wrapper

    return func


def use_bots(method):
    """Checks to see if a user has been authenticated"""

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if options.use_bots:
            return method(self, *args, **kwargs)
        else:
            self.render("public/404.html")

    return wrapper


def use_black_market(method):
    """Checks to see if a user has been authenticated"""

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if options.use_black_market:
            return method(self, *args, **kwargs)
        else:
            self.render("public/404.html")

    return wrapper
