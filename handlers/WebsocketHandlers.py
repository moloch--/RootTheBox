'''
Created on Mar 15, 2012

@author: haddaway
'''
import logging #@UnusedImport
import tornado.websocket #@UnresolvedImport
from libs.SecurityDecorators import * #@UnusedWildImport
from libs.WebSocketManager import WebSocketManager

class NotificationHandler(tornado.websocket.WebSocketHandler):
    
    def open(self): #@ReservedAssignment
        logging.info("WebSocket opened")
        manager = WebSocketManager.Instance() #@UndefinedVariable
        manager.add_connection(self)
        
    def on_message(self, message):
        logging.info("Someone Tried to send us ["+message+"]!")
        logging.info("User:"+self.get_current_user().__str__())
    
    def on_close(self):
        manager = WebSocketManager.Instance() #@UndefinedVariable
        manager.remove_connection(self)
        logging.info("WebSocket closed")
        