'''
Created on Mar 13, 2012

@author: moloch
'''

import functools
import datetime
from libs import sessions
from models.User import User

def authenticated(method):
    ''' Checks to see if a user has authenticated '''
    
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        sid = self.get_secure_cookie('auth')
        if sid != None:
            session = sessions[sid]
            if not datetime.timedelta(0) < (session.expiration - datetime.datetime.now()):
                del self.application.sessions[sid]
                self.redirect(self.application.settings['login_url'])
            if User.by_user_name(session.data['user_name']) != None:
                return method(self, *args, **kwargs)
        self.redirect(self.application.settings['login_url'])
    return wrapper

def authorized(permission):
    """ Checks user's permissions """
    
    def func(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            sid = self.get_secure_cookie('auth')
            if sid != None:
                session = sessions[sid]
                user = User.by_user_name(session.data['user_name'])
                if user != None and user.has_permission(permission):
                    return method(*args, **kwargs)
            self.redirect(self.application.settings['forbidden_url'])
        return wrapper
    return func