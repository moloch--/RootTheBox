'''
Created on Mar 15, 2012

@author: haddaway
'''
import tornado.websocket
from libs.SecurityDecorators import * #@UnusedWildImport
import logging
from modules.WebSocketManager import WebSocketManager

class NotificationHandler(tornado.websocket.WebSocketHandler):
    
    def open(self):
        logging.info("WebSocket opened")
        manager = WebSocketManager.Instance()
        manager.addConnection(self)
        
    def on_message(self, message):
        logging.info("Someone Tried to send us ["+message+"]!")
        logging.info("User:"+self.get_current_user().__str__())
    
    def on_close(self):
        manager = WebSocketManager.Instance()
        manager.removeConnection(self)
        logging.info("WebSocket closed")
        