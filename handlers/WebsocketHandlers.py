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
        manager = WebSocketManager.Instance() #@UndefinedVariable
        manager.add_connection(self)
        
    def on_message(self, message):
        logging.warn("%s tried to send us [%s]!" % (self.request.remote_ip, message))
    
    def on_close(self):
        manager = WebSocketManager.Instance() #@UndefinedVariable
        manager.remove_connection(self)
        