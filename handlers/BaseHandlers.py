'''
Created on Mar 15, 2012

@author: moloch
'''

from models import User
from libs.SecurityDecorators import *
from libs.Session import SessionManager
from tornado.web import RequestHandler #@UnresolvedImport

class UserBaseHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
        self.session_manager = SessionManager.Instance()
        self.session = self.session_manager.get_session(self.get_secure_cookie('auth'), self.request.remote_ip)
    
    def get_current_user(self):
        if self.session != None:
            return User.by_user_name(self.session.data['user_name'])
        return None


class AdminBaseHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
        self.get_functions = {
            'challenge':self.get_challenge,
            'action': self.get_action, 
            'team': self.get_team, 
            'user': self.get_user,
            'box': self.get_box, 
            'crackme': self.get_crack_me, 
            'se': self.get_se
        }
        self.post_functions = {
            'challenge':self.post_challenge,
            'action': self.post_action, 
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
