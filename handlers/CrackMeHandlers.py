'''
Created on Mar 13, 2012

@author: moloch
'''

from libs import sessions
from libs.SecurityDecorators import authenticated
from models import User
from tornado.web import RequestHandler #@UnresolvedImport

class CrackMeHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
    
    @authenticated
    def get(self, *args, **kwargs):
        session = sessions[self.get_secure_cookie('auth')]
        user = User.by_user_name(session.data['user_name'])
        self.render('crack_me/view.html', crack_me = user.team.crack_me)