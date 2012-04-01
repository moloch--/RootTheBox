'''
Created on Mar 15, 2012

@author: haddaway
'''

from tornado.web import RequestHandler #@UnresolvedImport
from models.Team import Team
from libs.WebSocketManager import WebSocketManager

class ScoreBoardHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
        
    def get(self, *args, **kwargs):
        ''' Display the scoreboard Page '''
        self.render('scoreboard/view.html', teams = Team.get_all(), cached_scores = WebSocketManager.Instance().cachedScores)
