'''
Created on Mar 13, 2012

@author: moloch
'''
from tornado.web import RequestHandler #@UnresolvedImport

class AdminHomeHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
    
    def get(self, *args, **kwargs):

        ''' Display the default user page '''
        self.render('admin/admin.html', header='User Page')