'''
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
'''


import logging
import functools

from threading import Thread
from models.User import User


def authenticated(method):
    ''' Checks to see if a user has been authenticated '''

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.session is not None:
            if self.session.ip_address == self.request.remote_ip:
                if not self.get_current_user().locked: 
                    return method(self, *args, **kwargs)
                else:
                    self.session.delete()
                    self.clear_all_cookies()
                    self.redirect('/403?locked=true')
            else:
                logging.warn("Session hijack attempt from %s?" % (
                    self.request.remote_ip,
                ))
                self.redirect(self.application.settings['login_url'])
        else:
            self.redirect(self.application.settings['login_url'])
    return wrapper


def restrict_ip_address(method):
    ''' Only allows access to ip addresses in a provided list '''

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.request.remote_ip in self.application.settings['admin_ips']:
            return method(self, *args, **kwargs)
        else:
            logging.warn("Attempted unauthorized access from %s to %s" % (
                self.request.remote_ip, self.request.uri,
            ))
            self.redirect(self.application.settings['forbidden_url'])
    return wrapper


def authorized(permission):
    ''' Checks user's permissions '''

    def func(method):

        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if self.session is not None:
                user = User.by_handle(self.session['handle'])
                if user is not None and user.has_permission(permission):
                    return method(self, *args, **kwargs)
            logging.warn("Attempted unauthorized access from %s to %s" % (
                self.request.remote_ip, self.request.uri,
            ))
            self.redirect(self.application.settings['forbidden_url'])
        return wrapper
    return func


def restrict_origin(method):
    ''' Check the origin header / prevent CSRF+WebSocket '''

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.request.headers['Origin'] == self.config.origin:
            return method(self, *args, **kwargs)
    return wrapper


def async(method):
    ''' Quick and easy async functions'''

    @functools.wraps(method)
    def __async__(*args, **kwargs):
        worker = Thread(target=method, args=args, kwargs=kwargs)
        worker.start()


def debug(method):
    ''' Logs a method call/return '''

    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        class_name = args[0].__class__.__name__
        logging.debug("Call to -> %s.%s()" % (
            class_name, method.__name__,
        ))
        value = method(*args, **kwargs)
        logging.debug("Return from <- %s.%s()" % (
            class_name, method.__name__,
        ))
        return value
    return wrapper


def has_item(name):
    ''' Checks user's team owns an unlock/item '''

    def func(method):

        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            user = self.get_current_user()
            if user is not None and user.has_item(name):
                return method(self, *args, **kwargs)
            else:
                logging.warn("Attempted unauthorized access from %s to %s" % (
                    self.request.remote_ip, self.request.uri,
                ))
                self.redirect(self.application.settings['forbidden_url'])
        return wrapper
    return func
