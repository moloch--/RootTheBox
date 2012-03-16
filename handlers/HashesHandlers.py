'''
Created on Mar 15, 2012

@author: moloch
'''

from libs.SecurityDecorators import authenticated
from models import Team, User, Action
from handlers.BaseHandlers import UserBaseHandler

class HashesHandler(UserBaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        ''' Renders hashes page '''
        user = User.by_user_name(self.get_current_user())
        self.render("hashes/view.html", teams = Team.get_all(), current = user.team)
    
    @authenticated
    def post(self, *args, **kwargs):
        ''' Submit cracked hashes get checked '''
        
        # Get target display_name
        try:
            display_name = self.get_argument("display_name")
        except:
            self.render("hashes/error.html", errors = "No user name")
        
        # Get preimage
        try:
            preimage = self.get_argument("preimage")
        except:
            self.render("hashes/error.html", errors = "No password")
            
        user = User.by_user_name(self.session['user_name'])
        target = User.by_display_name(display_name)
        
        if target == None or target.has_permission("admin"):
            self.render("hashes/error.html", operation = "hash cracking", errors = "That user does not exist")
        if user in user.team.members:
            self.render("hashes/error.html", operation = "hash cracking", errors = "You can't crack hashes from your own team")
        if target.validate_password(preimage):
            self.steal_points(user, target)
            self.render("hashes/success.html", user = user, target = target )
        else:
            self.render("hashes/error.html", operation = "hash cracking", errors = "Wrong password")
            
    def steal_points(self, user, target):
        ''' Creates actions if password cracking was successful '''
        user_action = Action (
            classification = unicode("Hash Cracking"),
            description = unicode("%s cracked %s's password" % (user.display_name, target.display_name)),
            value = target.score,
            user_id = user.id
        )
        target_action = Action (
            classification = unicode("Hash Cracking"),
            description = unicode("%s's password was cracked by %s" % (target.display_name, user.display_name)),
            value = (target.score * -1),
            user_id = target.id
        )
        self.dbsession.add(target_action)
        self.dbsession.add(user_action)
        self.dbsession.flush()
