'''
Created on Mar 13, 2012

@author: moloch
'''

import functools
from json import loads
from models.User import User

def authenticated(method):
    ''' Checks to see if a user has authenticated '''
    
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        auth = loads(self.get_secure_cookie('auth') or '""')
        print 'Got:', auth
        if User.by_user_name(auth['user_name']) != None:
            return method(self, *args, **kwargs)
        else:
            self.redirect(self.application.settings['login_url'])
    return wrapper


def authorized(method):
    """ Checks user's permissions """
    
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        self.redirect(self.application.settings['forbidden_url'])
    return wrapper