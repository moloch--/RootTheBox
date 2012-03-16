'''
Created on Mar 15, 2012

@author: haddaway
'''
from libs.Singleton import *

@Singleton
class WebSocketManager():
    
    def __init__(self):
        self.connections = []
        
    def send_all(self, notification):
        for connection in self.connections:
            connection.write_message(notification.to_message())
    
    def add_connection(self, connection): 
        self.connections.append(connection)
    
    def remove_connection(self, connection):
        self.connections.remove(connection)