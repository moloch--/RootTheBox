'''
Created on Mar 13, 2012

@author: moloch
'''

import logging
import functools
from models.User import User
from libs.Session import SessionManager

def authenticated(method):
    ''' Checks to see if a user has been authenticated '''
    
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        session_manager = SessionManager.Instance()
        session = session_manager.get_session(self.get_secure_cookie('auth'), self.request.remote_ip)
        if session != None:
            return method(self, *args, **kwargs)
        self.redirect(self.application.settings['login_url'])
    return wrapper

def restrict_ip_address(method):
    """ Only allows access to ip addresses in a provided list """
    
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.request.remote_ip in self.application.settings['admin_ips']:
            return method(self, *args, **kwargs)
        else:
            logging.warn("Attempted unauthorized access from %s to %s" % (self.request.remote_ip, self.request.uri))
            self.redirect(self.application.settings['forbidden_url'])
    return wrapper


def authorized(permission):
    """ Checks user's permissions """
    
    def func(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            session_manager = SessionManager.Instance()
            session = session_manager.get_session(self.get_secure_cookie('auth'), self.request.remote_ip)
            if session != None:
                user = User.by_user_name(session.data['user_name'])
                if user != None and user.has_permission(permission):
                    return method(self, *args, **kwargs)
            logging.warn("Attempted unauthorized access from %s to %s" % (self.request.remote_ip, self.request.uri))
            self.redirect(self.application.settings['forbidden_url'])
        return wrapper
    return func
