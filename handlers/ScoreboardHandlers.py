# -*- coding: utf-8 -*-
'''
Created on Mar 15, 2012

@author: haddaway

 Copyright [2012] [Redacted Labs]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''

from tornado.web import RequestHandler  # @UnresolvedImport
from models.Team import Team
from libs.WebSocketManager import WebSocketManager


class ScoreBoardHandler(RequestHandler):

    def initialize(self, dbsession):
        self.dbsession = dbsession

    def get(self, *args, **kwargs):
        ''' Display the scoreboard Page '''
        self.render('scoreboard/view.html', teams=Team.get_all(
        ), cached_scores=WebSocketManager.Instance().cachedScores)


class AllTimeHandler(RequestHandler):
    def initialize(self, dbsession):
        self.dbsession = dbsession

    def get(self, *args, **kwargs):
        ''' Display the All Time Page '''
        self.render('scoreboard/all_time.html', teams=Team.get_all(
        ), cached_scores=WebSocketManager.Instance().cachedScores)


class PieChartHandler(RequestHandler):
    def initialize(self, dbsession):
        self.dbsession = dbsession

    def get(self, *args, **kwargs):
        ''' Display the Pie Chart Page '''
        self.render('scoreboard/pie_chart.html', teams=Team.get_all(
        ), cached_scores=WebSocketManager.Instance().cachedScores)


class BarChartHandler(RequestHandler):
    def initialize(self, dbsession):
        self.dbsession = dbsession

    def get(self, *args, **kwargs):
        ''' Display the Bar Chart Page '''
        self.render('scoreboard/bar_chart.html', teams=Team.get_all(
        ), cached_scores=WebSocketManager.Instance().cachedScores)
