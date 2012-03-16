'''
Created on Mar 15, 2012

@author: haddaway
'''
from libs.SecurityDecorators import authenticated
from tornado.web import RequestHandler #@UnresolvedImport

class ScoreBoardHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
        
    def get(self):
        ''' Display the scoreboard Page '''
        self.render('scoreboard/view.html')
