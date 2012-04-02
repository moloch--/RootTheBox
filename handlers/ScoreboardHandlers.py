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

class AllTimeHandler(RequestHandler):
    def initialize(self, dbsession):
        self.dbsession = dbsession
        
    def get(self, *args, **kwargs):
        ''' Display the All Time Page '''
        self.render('scoreboard/all_time.html', teams = Team.get_all(), cached_scores = WebSocketManager.Instance().cachedScores)

class PieChartHandler(RequestHandler):
    def initialize(self, dbsession):
        self.dbsession = dbsession
        
    def get(self, *args, **kwargs):
        ''' Display the Pie Chart Page '''
        self.render('scoreboard/pie_chart.html', teams = Team.get_all(), cached_scores = WebSocketManager.Instance().cachedScores)

class BarChartHandler(RequestHandler):
    def initialize(self, dbsession):
        self.dbsession = dbsession
        
    def get(self, *args, **kwargs):
        ''' Display the Bar Chart Page '''
        self.render('scoreboard/bar_chart.html', teams = Team.get_all(), cached_scores = WebSocketManager.Instance().cachedScores)
