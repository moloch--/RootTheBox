'''
Created on Mar 13, 2012

@author: moloch
'''

#import logging

from uuid import uuid1
from tornado.web import RequestHandler #@UnresolvedImport
from libs.SecurityDecorators import * #@UnusedWildImport
from models import Team, Box, CrackMe

class AdminHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
        self.get_functions = {
            'team': self.get_team, 
            'user': self.get_user,
            'box': self.get_box, 
            'crackme': self.get_crack_me, 
            'se': self.get_se
        }
        self.post_functions = {
            'team': self.post_team,
            'user': self.post_user,
            'box': self.post_box, 
            'crackme': self.post_crack_me, 
            'se': self.post_se
        }
    
    @authorized('admin')
    @restrict_ip_address
    def get(self, *args, **kwargs):
        if args[0] in self.get_functions.keys():
            self.get_functions[args[0]](*args, **kwargs)
        else:
            self.render("admin/unknown_object.html", unknown_object = args[0])
    
    @authorized('admin')
    @restrict_ip_address
    def post(self, *args, **kwargs):
        if args[0] in self.post_functions.keys():
            self.post_functions[args[0]](*args, **kwargs)
        else:
            self.render("admin/unknown_object.html", unknown_object = args[0])

class AdminCreateHandler(AdminHandler):

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
        self.render("admin/created.html", game_object='team')
    
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
            file_uuid = uuid1()
            token = self.get_argument('token')
        except:
            self.render("admin/error.html", errors = "Failed to create crack me")
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
        
    

class AdminEditHandler(AdminHandler):
    
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