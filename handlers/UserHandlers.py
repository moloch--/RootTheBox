'''
Created on Mar 13, 2012

@author: moloch
'''

import imghdr
import logging

from uuid import uuid1
from models import User
from libs.Session import SessionManager
from libs.SecurityDecorators import authenticated
from tornado.web import RequestHandler
from BaseHandlers import UserBaseHandler

class HomeHandler(UserBaseHandler):
    
    @authenticated
    def get(self, *args, **kwargs):
        ''' Display the default user page '''
        user = User.by_user_name(self.session.data['user_name'])
        self.render('user/home.html', user = user)

class SharesHandler(UserBaseHandler):

    def get(self, *args, **kwargs):
        pass
    
    def post(self, *args, **kwargs):
        pass

class SettingsHandler(RequestHandler):
    
    def initialize(self, dbsession):
        ''' Database and URI setup '''
        self.dbsession = dbsession
        self.session_manager = SessionManager.Instance()
        self.session = self.session_manager.get_session(self.get_secure_cookie('auth'), self.request.remote_ip)
        self.post_functions = {
            '/avatar': self.post_avatar,
            '/changepassword': self.post_password
        }
    
    @authenticated
    def get(self, *args, **kwargs):
        ''' Display the user settings '''
        user = User.by_user_name(self.session.data['user_name'])
        self.render('user/settings.html', user = user)
    
    @authenticated
    def post(self, *args, **kwargs):
        ''' Calls function based on parameter '''
        if args[0] in self.post_functions.keys():
            self.post_functions[args[0]](*args, **kwargs)
        else:
            self.render("user/error.html")
    
    def post_avatar(self, *args, **kwargs):
        ''' Saves avatar - Reads file header an only allows approved formats '''
        user = User.by_user_name(self.session.data['user_name'])
        if self.request.files.has_key('avatar') and len(self.request.files['avatar']) == 1:
            if len(self.request.files['avatar'][0]['body']) < (1024*1024):
                if user.avatar == "default_avatar.gif":
                    user.avatar = unicode(str(uuid1()))
                ext = imghdr.what("", h = self.request.files['avatar'][0]['body'])
                if ext in ['png', 'jpeg', 'gif', 'bmp']:
                    user.avatar = user.avatar[:user.avatar.rfind('.')]+"."+ext
                    file_path = self.application.settings['avatar_dir']+'/'+user.avatar
                    avatar = open(file_path, 'wb')
                    avatar.write(self.request.files['avatar'][0]['body'])
                    avatar.close()
                    self.dbsession.add(user)
                    self.dbsession.flush()
                    self.redirect("/user")
                else:
                    self.render("user/error.html", operation = "Uploading avatar", errors = "Invalid image format")
            else:
                self.render("user/error.html", operation = "Uploading avatar", errors = "The image is too large")
        else:
            self.render("user/error.html", operation = "Uploading avatar", errors = "Please provide and image")

    def post_password(self, *args, **kwargs):
        pass
        
class LogoutHandler(UserBaseHandler):

    def get(self, *args, **kwargs):
        ''' Clears cookies and session data '''
        self.session_manager.remove_session(self.get_secure_cookie('auth'))
        self.clear_all_cookies()
        self.redirect("/")
