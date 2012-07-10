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
import logging
import tornado.websocket
from libs.SecurityDecorators import *
from libs.WebSocketManager import WebSocketManager

class WebsocketHandler(tornado.websocket.WebSocketHandler):
    
    def open(self):
        self.manager = WebSocketManager.Instance() 
        self.manager.add_connection(self)
        
    def on_message(self, message):
        if message == "load plox":
            self.manager.get_updates(self)
            self.write_message("{\"redraw\":\"true\"}")
        else:
            logging.warn("%s tried to send us '%s'" % (self.request.remote_ip, message))

    def on_close(self):
        self.manager.remove_connection(self)
