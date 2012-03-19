'''
Created on Mar 15, 2012

@author: haddaway
'''
from libs.Singleton import *
import logging
from libs.Session import SessionManager
import models

@Singleton
class WebSocketManager():
    
    def __init__(self):
        self.connections = []
        self.currentUpdates = []
        
    def get_updates(self, connection):
        for update in self.currentUpdates:
            connection.write_message(update.to_message())
        
    def send_all(self, update):
        for connection in self.connections:
            connection.write_message(update.to_message())
    
    def send_user(self, user, update):
        ''' Sends a targeted user a specific message '''
        self.session_manager = SessionManager.Instance()
        for connection in self.connections:
            try:
                session = self.session_manager.get_session(self.connections[0].get_secure_cookie('auth'), self.connections[0].request.remote_ip)
                current_user = models.User.by_user_name(session.data['user_name'])
                if(user == current_user):
                    connection.write_message(update.to_message())
            except:
                ''' These happen because a user can have a websocket connection and not be logged in'''
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