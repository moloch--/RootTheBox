'''
Created on Mar 13, 2012

@author: moloch
'''

from models.Box import Box
from tornado.web import RequestHandler #@UnresolvedImport

class BoxesViewHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
        
    def get(self, *args, **kwargs):
        self.render("boxes/boxes_view.html", boxes = Box.get_all())