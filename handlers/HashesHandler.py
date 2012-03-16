'''
Created on Mar 15, 2012

@author: moloch
'''

#from libs import sessions
from libs.SecurityDecorators import authenticated
#from models import User
from tornado.web import RequestHandler #@UnresolvedImport

class HashesHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
        
    @authenticated
    def get(self):
        pass
