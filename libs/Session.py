'''
Created on Mar 13, 2012

@author: moloch
'''

from datetime import datetime, timedelta

class Session(object):
    
    def __init__(self):
        self.id = ''
        self.data = {}
        self.expiration = datetime.now() + timedelta(minutes = 20)
    
    def is_expired(self):
    	''' Returns boolean based on if session has expired '''
        return (timedelta(0) < (datetime.now() - self.expiration))
