'''
Created on Mar 13, 2012

@author: moloch
'''

from tornado.web import RequestHandler #@UnresolvedImport

class HomeHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
    
    def get(self, *args, **kwargs):
        ''' Display the default user page '''
        self.render('user.html', header='User Page')
    
class SettingsHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
    
    def get(self, *args, **kwargs):
        ''' Display the user settings '''
        self.render('user_settings.html', header='User Settings')
    
class TeamHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
    
    def get(self, *args, **kwargs):
        pass
    
class BoxesHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
    
    def get(self, *args, **kwargs):
        pass
    
class ScoreBoardHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
    
    def get(self, *args, **kwargs):
        pass