'''
Created on Mar 13, 2012

@author: moloch
'''

from tornado.web import RequestHandler #@UnresolvedImport
from tornado.web import asynchronous #@UnresolvedImport

class HomeHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
    
    @asynchronous
    def get(self, *args, **kwargs):
        pass
    
class SettingsHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
    
    @asynchronous
    def get(self, *args, **kwargs):
        pass