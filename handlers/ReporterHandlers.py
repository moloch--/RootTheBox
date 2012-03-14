'''
Created on Mar 13, 2012

@author: moloch
'''

from tornado.web import RequestHandler #@UnresolvedImport
from tornado.web import asynchronous #@UnresolvedImport

class ReporterRegistrationHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
    
    def get(self):
        self.render("404.html")
    
    @asynchronous
    def post(self):
        self.write("Hello World")
        self.finish()
