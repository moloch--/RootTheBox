'''
Created on Mar 13, 2012

@author: moloch
'''

from models.Box import Box
from libs.SecurityDecorators import authenticated
from tornado.web import RequestHandler #@UnresolvedImport

class BoxesViewHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
    
    @authenticated
    def get(self, *args, **kwargs):
        self.render("boxes/view.html", boxes = Box.get_all())