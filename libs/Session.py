'''
Created on Mar 13, 2012

@author: moloch
'''

import datetime

class Session(object):
    
    def __init__(self):
        self.data = {}
        self.expiration = datetime.datetime.now() + datetime.timedelta(minutes = 20)