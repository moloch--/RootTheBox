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
import models
import logging
from libs.Singleton import *
from libs.Session import SessionManager
from libs.CachedScores import CachedScores
import tornado

@Singleton
class WebSocketManager():
    
    def __init__(self):
        self.connections = []
        self.currentUpdates = []
        self.cachedScores = CachedScores()
        
    def get_updates(self, connection):
        totalMessage = ''
        for update in self.currentUpdates:
            totalMessage += tornado.escape.json_encode(update.to_message()) + '\n'
        connection.write_message(totalMessage)
            
    def send_all(self, update):
        for connection in self.connections:
            connection.write_message(update.to_message())
    
    def send_user(self):
        pass

    def send_team(self):
        pass

    def send_team(self, team, update):
        ''' sends an entire team a specific message '''
        self.session_manager = SessionManager.Instance()
        for connection in self.connections:
            try:
                session = self.session_manager.get_session(self.connections[0].get_secure_cookie('auth'), self.connections[0].request.remote_ip)
                current_user = models.User.by_user_name(session.data['user_name'])
                if(current_user.team == team):
                    logging.info("Sending!")
                    connection.write_message(update.to_message())
            except:
                ''' These happen because a user can have a websocket connection and not be logged in'''
                pass
        
    def add_connection(self, connection): 
        self.connections.append(connection)

    def remove_connection(self, connection):
        self.connections.remove(connection)
