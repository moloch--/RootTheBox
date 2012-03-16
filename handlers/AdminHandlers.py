'''
Created on Mar 13, 2012

@author: moloch
'''

import logging #@UnusedImport

from uuid import uuid1
from libs.SecurityDecorators import * #@UnusedWildImport
from libs.WebSocketManager import WebSocketManager
from models import Team, Box, CrackMe, Action
from handlers.BaseHandlers import AdminBaseHandler
from tornado.web import RequestHandler #@UnresolvedImport
from libs.Notification import Notification
import base64

class AdminCreateHandler(AdminBaseHandler):
    
    def get_action(self, *args, **kwargs):
        self.render("admin/create_action.html", users = User.get_all())
        
    def post_action(self, *args, **kwargs):
        try:
            classification = self.get_argument("classification")
            description = self.get_argument("description")
            value = int(self.get_argument("value"))
            user_name = self.get_argument("user_name")
        except:
            self.render("admin/error.html", errors = "Failed to create action")
        user = User.by_user_name(user_name)
        action = Action(
            classification = unicode(classification),
            description = unicode(description),
            value = value,
            user_id = user.id
        )
        user.dirty = True
        self.dbsession.add(action)
        self.dbsession.add(user)
        self.dbsession.flush()
        self.render("admin/created.html", game_object = "action")
        
        
    def get_team(self, *args, **kwargs):
        self.render("admin/create_team.html")
        
    def post_team(self, *args, **kwargs):
        try:
            team_name = self.get_argument('team_name')
            motto = self.get_argument('motto')
        except:
            self.render("admin/error.html", errors = "Failed to create team")
        team = Team(
            team_name = unicode(team_name),
            motto = unicode(motto)
        )
        self.dbsession.add(team)
        self.dbsession.flush()
        self.render("admin/created.html", game_object = 'team')
    
    def get_user(self, *args, **kwargs):
        pass
    
    def post_user(self, *args, **kwargs):
        pass
    
    def get_box(self, *args, **kwargs):
        self.render("admin/create_box.html")
    
    def post_box(self, *args, **kwargs):
        try:
            box_name = self.get_argument("box_name")
            ip_address = self.get_argument("ip_address")
            description = self.get_argument("description")
            root_key = self.get_argument("root_key")
            root_value = int(self.get_argument("root_value"))
            user_key = self.get_argument("user_key")
            user_value = int(self.get_argument("user_value"))
        except:
            self.render("admin/error.html", errors = "Failed to create box")
        box = Box(
            box_name = unicode(box_name),
            ip_address = unicode(ip_address),
            description = unicode(description),
            root_key = unicode(root_key),
            root_value = root_value,
            user_key = unicode(user_key),
            user_value = user_value
        )
        self.dbsession.add(box)
        self.dbsession.flush()
        self.render("admin/created.html", game_object = "box")
        
    def get_crack_me(self, *args, **kwargs):
        self.render("admin/create_crackme.html")
    
    def post_crack_me(self, *args, **kwargs):
        try:
            crack_me_name = self.get_argument('crack_me_name')
            description = self.get_argument('description')
            value = int(self.get_argument('value'))
            file_name = self.get_argument('file_name')
            file_uuid = str(uuid1())
            token = self.get_argument('token')
            if len(self.request.files['crack_me']) != 1: raise TypeError
        except:
            self.render("admin/error.html", errors = "Failed to create crack me")
        filePath = self.application.settings['crack_me_dir']+'/'+file_uuid
        save = open(filePath, 'wb')
        save.write(self.request.files['crack_me'][0]['body'])
        save.close()
        crack_me = CrackMe(
            crack_me_name = unicode(crack_me_name),
            description = unicode(description),
            value = value,
            file_name = unicode(file_name),
            file_uuid = unicode(file_uuid),
            token = unicode(token)
        )
        self.dbsession.add(crack_me)
        self.dbsession.flush()
        self.render('admin/created.html', game_object = "crack me")
    
    def get_se(self, *args, **kwargs):
        pass
        
    def post_se(self, *args, **kwargs):
        self.render("admin/create_se.html")

class AdminEditHandler(AdminBaseHandler):
    
    def get_action(self, *args, **kwargs):
        pass
    
    def post_action(self, *args, **kwargs):
        pass
    
    def get_team(self, *args, **kwargs):
        pass
        
    def post_team(self, *args, **kwargs):
        pass
    
    def get_user(self, *args, **kwargs):
        self.render("admin/edit_user.html", teams = Team.get_all(), users = User.get_free_agents())
    
    def post_user(self, *args, **kwargs):
        try:
            team_name = self.get_argument('team_name')
            user_name = self.get_argument('user_name')
            team = Team.by_team_name(team_name)
            user = User.by_user_name(user_name)
            if team == None: raise TypeError
            if user == None: raise TypeError
        except:
            self.render("admin/error.html", errors = "Failed to edit user")
        user.team_id = team.id
        self.dbsession.add(user)
        self.dbsession.flush()
        self.render("admin/created.html", game_object = "edit user team")
        
    def get_box(self, *args, **kwargs):
        pass
        
    def post_box(self, *args, **kwargs):
        pass
    
    def get_crack_me(self, *args, **kwargs):
        pass
        
    def post_crack_me(self, *args, **kwargs):
        pass
    
    def get_se(self, *args, **kwargs):
        pass
        
    def post_se(self, *args, **kwargs):
        pass

class AdminNotifyHandler(RequestHandler):
    
    def initialize(self):
        self.ws_manager = WebSocketManager.Instance() #@UndefinedVariable
    
    @authorized("admin")
    @restrict_ip_address
    def get(self, *args, **kwargs):
        self.render("admin/notify.html", classifications = Notification.get_classifications())
    
    @authorized("admin")
    @restrict_ip_address
    def post(self, *args, **kwargs):
        try:
            message = self.get_argument("message")
            title = self.get_argument("title") #@UnusedVariable
            classification = self.get_argument("classification")
            try:
                file_contents = base64.encodestring(self.request.files['image'][0]['body'])
            except:
                file_contents = None
        except:
            self.render("admin/error.html", errors = "Invalid Entry")
        if file_contents == None:
            notification = Notification(title, message, classification)
        else:
            notification = Notification(title, message, file_contents = file_contents)
        self.ws_manager.send_all(notification)
        logging.info("Admin sent a notification")
        self.redirect("/admin/notify")
        
            
            