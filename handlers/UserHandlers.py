'''
Created on Mar 13, 2012

@author: moloch
'''

import logging

from libs import sessions
from libs.SecurityDecorators import authenticated
from models import User
from tornado.web import RequestHandler #@UnresolvedImport

class HomeHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
    
    @authenticated
    def get(self, *args, **kwargs):
        ''' Display the default user page '''
        session = sessions[self.get_secure_cookie('auth')]
        user = User.by_user_name(session.data['user_name'])
        self.render('user/home.html', user = user)

class SettingsHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
    
    @authenticated
    def get(self, *args, **kwargs):
        ''' Display the user settings '''
        session = sessions[self.get_secure_cookie('auth')]
        user = User.by_user_name(session.data['user_name'])
        self.render('user/settings.html', user = user)

class LogoutHandler(RequestHandler):
    
    def get(self, *args, **kwargs):
        logging.info("User logout")
        try:
            sid = self.get_secure_cookie('auth')
            if sessions.has_key(sid):
                del sessions[sid]
        except:
            pass
        self.clear_all_cookies()
        self.redirect("/")
