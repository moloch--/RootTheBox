'''
Created on Mar 13, 2012

@author: moloch
'''

import functools

def authenticated(method):
    ''' Checks to see if a user has authenticated '''
    
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        self.get_secure_cookie('auth')
        
        self.redirect(self.application.settings['login_url'])
    return wrapper


def authorized(method):
    """ Checks user's permissions """
    
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        self.redirect(self.application.settings['forbidden_url'])
    return wrapper