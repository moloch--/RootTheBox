'''
Created on Mar 15, 2012

@author: haddaway
'''
from libs.Singleton import *

@Singleton
class WebSocketManager():
    
    def __init__(self):
        self.connections = []
        
    def sendClientsNotification(self, notificationMessage, notificationType):
        for connection in self.connections:
            connection.write_message(notificationType+":"+notificationMessage)
    
    def addConnection(self, connection): 
        self.connections.append(connection)
    
    def removeConnection(self, connection):
        self.connections.remove(connection)