'''
Created on Mar 15, 2012

@author: moloch
'''

from libs.SecurityDecorators import authenticated
from models import Team, User
from handlers.BaseHandlers import UserBaseHandler

class HashesHandler(UserBaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        user = User.by_user_name(self.get_current_user())
        self.render("hashes/view.html", teams = Team.get_all(), current = user.team)
    
    @authenticated
    def post(self, *args, **kwargs):
        try:
            display_name = self.get_argument("display_name")
        except:
            self.render("hashes/error.html", errors = "No user name")
        try:
            preimage = self.get_argument("preimage")
        except:
            self.render("hashes/error.html", errors = "No password")
            
        user = User.by_user_name(self.session['user_name'])
        target = User.by_display_name(display_name)
        
        if target == None or target.has_permission("admin") or target.id == user.id:
            self.render("hashes/error.html", errors = "User does not exist")
        if target.validate_password(preimage):
            self.steal_points(user, target)
            self.render("hashes/success.html", )
        else:
            self.render("hashes/error.html", errors = "Wrong password")
            
    def steal_points(self, user, target):
        pass
