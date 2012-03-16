'''
Created on Mar 13, 2012

@author: moloch
'''

from models import 
from libs.Notification import Notification
from libs.WebSocketManager import WebSocketManager
from tornado.web import RequestHandler #@UnresolvedImport
from tornado.web import asynchronous #@UnresolvedImport

class ReporterRegistrationHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
    
    @asynchronous
    def get(self, *args, **kwargs):
    	box = Box.by_ip_address(self.request.remote_ip)
    	if box != None:
    		try:
		    	user = User.by_display_name(self.get_argument("handle"))
		    	if user != None:
		    		user.team.controlled_boxes.append(box)
		    		self.dbsession.add(user)
		    		self.dbsession.flush()
		    		self.notify(user, box)
		    		self.write(user.team.listen_port)
		    	else:
		    		self.write("Invalid handle")
		    except:
		    	self.write("Missing parameter")
	    else:
	        self.write("Invalid ip address")
	    self.finish()

	def notify(self, user, box):
		title = "Box Owned!"
		message = "%s owned %s" % (user.display_name, box.box_name)
		notify = Notification(title, message, file_location = self.application.settings['avatar_dir']+'/'+user.avatar)
		ws_manager = WebSocketManager.Instance()
		ws_manager.send_all(notify)
