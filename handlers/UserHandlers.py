'''
Created on Mar 13, 2012

@author: moloch
'''

import logging

from uuid import uuid1
from libs.SecurityDecorators import authenticated
from models import User
from BaseHandlers import UserBaseHandler

class HomeHandler(UserBaseHandler):
    
    @authenticated
    def get(self, *args, **kwargs):
        ''' Display the default user page '''
        user = User.by_user_name(self.session.data['user_name'])
        self.render('user/home.html', user = user)

class SharesHandler(UserBaseHandler):
    
    def initialize(self, dbsession):
        self.dbsession
    
    def get(self, *args, **kwargs):
        pass
    
    def post(self, *args, **kwargs):
        pass

class SettingsHandler(UserBaseHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
        self.post_functions = {
            '/avatar': self.post_avatar
        }
    
    @authenticated
    def get(self, *args, **kwargs):
        ''' Display the user settings '''
        user = User.by_user_name(self.session.data['user_name'])
        self.render('user/settings.html', user = user)
    
    @authenticated
    def post(self, *args, **kwargs):
        if args[0] in self.post_functions.keys():
            self.post_functions[args[0]](*args, **kwargs)
        else:
            self.render("user/error.html")
    
    def post_avatar(self, *args, **kwargs):
        ''' Saves avatar - does NOT currently validate file type '''
        user = User.by_user_name(self.session.data['user_name'])
        if self.request.files.has_key('avatar') and len(self.request.files['avatar']) == 1:
            if len(self.request.files['avatar'][0]['body']) < (1024*1024):
                if user.avatar == None:
                    user.avatar = unicode(str(uuid1()) + '.jpg')
                filePath = self.application.settings['avatar_dir']+'/'+user.avatar
                logging.info("Saving avatar to: %s" % filePath)
                avatar = open(filePath, 'wb')
                avatar.write(self.request.files['avatar'][0]['body'])
                avatar.close()
                self.dbsession.add(user)
                self.dbsession.flush()
                self.redirect("/user")
        else:
            self.render("user/error.html")
        
class LogoutHandler(UserBaseHandler):
    
    def get(self, *args, **kwargs):
        ''' Clears cookies and session data '''
        try:
            sid = self.get_secure_cookie('auth')
            if self.sessions.has_key(sid):
                logging.info("User logout: %s" % self.sessions[sid].data['user_name'])
                del self.sessions[sid]
        except:
            pass
        self.clear_all_cookies()
        self.redirect("/")
