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
        self.render('user/home.html', header='Welcome ' + user.user_name)

class SettingsHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
    
    @authenticated
    def get(self, *args, **kwargs):
        ''' Display the user settings '''
        logging.info("Render user page")
        self.render('user/user_settings.html', header='User Settings')

class LogoutHandler(RequestHandler):
    
    def get(self, *args, **kwargs):
        logging.info("User logout")
        try:
            sid = self.get_secure_cookie('auth')
            del sessions[sid]
        except:
            pass
        self.clear_all_cookies()
        self.redirect("/")
