'''
Created on Mar 13, 2012

@author: moloch
'''

#import logging

from tornado.web import RequestHandler #@UnresolvedImport
from libs.SecurityDecorators import * #@UnusedWildImport

class AdminHomeHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
    
    @authorized('admin')
    @restrict_ip_address
    def get(self, *args, **kwargs):
        ''' Display the default user page '''
        self.render('admin/admin.html', header='Admin Page')

class AdminEditTeams(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
    
    @authorized('admin')
    @restrict_ip_address
    def get(self, *args, **kwargs):
        pass
    
    @authorized('admin')
    @restrict_ip_address
    def post(self, *args, **kwargs):
        pass

class AdminEditBoxes(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
    
    @authorized('admin')
    @restrict_ip_address
    def get(self, *args, **kwargs):
        pass
    
    @authorized('admin')
    @restrict_ip_address
    def post(self, *args, **kwargs):
        pass

class AdminEditUsers(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
    
    @authorized('admin')
    @restrict_ip_address
    def get(self, *args, **kwargs):
        pass
    
    @authorized('admin')
    @restrict_ip_address
    def post(self, *args, **kwargs):
        pass
